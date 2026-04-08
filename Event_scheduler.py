# event_scheduler.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import heapq
import bisect
import time


@dataclass
class Event:
    event_id: str
    title: str
    timestamp: float   # seconds since epoch or any comparable numeric
    priority: int      # higher = more important
    duration: float    # in seconds
    cancelled: bool = False  # for lazy deletion in heap


class EventScheduler:
    """
    Manages events using:
      - Heap:        for next-event retrieval (by timestamp, then priority)
      - Hash table:  for O(1) lookup by event_id
      - Ordered list:sorted by timestamp for range queries
    """

    def __init__(self) -> None:
        # event_id -> Event
        self._events: Dict[str, Event] = {}

        # heap of (timestamp, -priority, event_id)
        self._heap: List[Tuple[float, int, str]] = []

        # ordered by timestamp: list of (timestamp, event_id)
        self._ordered: List[Tuple[float, str]] = []

    # ---------------------------------------------------------
    # Internal helpers
    # ---------------------------------------------------------

    def _clean_heap(self) -> None:
        """Remove cancelled or stale events from the top of the heap."""
        while self._heap:
            ts, neg_prio, eid = self._heap[0]
            ev = self._events.get(eid)
            if ev is None or ev.cancelled or ev.timestamp != ts or -neg_prio != ev.priority:
                heapq.heappop(self._heap)
            else:
                break

    def _remove_from_ordered(self, event: Event) -> None:
        """Remove an event from the ordered timestamp list."""
        ts = event.timestamp
        eid = event.event_id
        # Find approximate position by timestamp
        idx = bisect.bisect_left(self._ordered, (ts, ""))
        while idx < len(self._ordered) and self._ordered[idx][0] == ts:
            if self._ordered[idx][1] == eid:
                self._ordered.pop(idx)
                return
            idx += 1

    # ---------------------------------------------------------
    # 1. add_event(...)
    # ---------------------------------------------------------

    def add_event(
        self,
        event_id: str,
        title: str,
        timestamp: float,
        priority: int,
        duration: float,
    ) -> Event:
        """Add a new event. Overwrites if event_id already exists."""
        # If exists, cancel old one first
        if event_id in self._events:
            self.cancel_event(event_id)

        ev = Event(
            event_id=event_id,
            title=title,
            timestamp=timestamp,
            priority=priority,
            duration=duration,
        )
        self._events[event_id] = ev

        # push to heap
        heapq.heappush(self._heap, (timestamp, -priority, event_id))

        # insert into ordered list
        bisect.insort(self._ordered, (timestamp, event_id))

        return ev

    # ---------------------------------------------------------
    # 2. cancel_event(...)
    # ---------------------------------------------------------

    def cancel_event(self, event_id: str) -> bool:
        """Cancel an event by id. Returns True if it existed."""
        ev = self._events.get(event_id)
        if not ev:
            return False
        ev.cancelled = True
        self._remove_from_ordered(ev)
        # Keep in dict until popped from heap? We can remove now:
        del self._events[event_id]
        return True

    # ---------------------------------------------------------
    # 3. update_priority(...)
    # ---------------------------------------------------------

    def update_priority(self, event_id: str, new_priority: int) -> bool:
        """Update the priority of an existing event."""
        ev = self._events.get(event_id)
        if not ev or ev.cancelled:
            return False

        ev.priority = new_priority
        # Push a new heap entry; old one will be cleaned lazily
        heapq.heappush(self._heap, (ev.timestamp, -ev.priority, ev.event_id))
        return True

    # ---------------------------------------------------------
    # 4. get_event(...)
    # ---------------------------------------------------------

    def get_event(self, event_id: str) -> Optional[Event]:
        """Return the event with the given id, or None."""
        return self._events.get(event_id)

    # ---------------------------------------------------------
    # 5. peek_next()
    # ---------------------------------------------------------

    def peek_next(self) -> Optional[Event]:
        """
        Return the next event (earliest timestamp, then highest priority)
        without removing it.
        """
        self._clean_heap()
        if not self._heap:
            return None
        _, _, eid = self._heap[0]
        return self._events.get(eid)

    # ---------------------------------------------------------
    # 6. pop_next()
    # ---------------------------------------------------------

    def pop_next(self) -> Optional[Event]:
        """
        Remove and return the next event.
        """
        self._clean_heap()
        if not self._heap:
            return None

        ts, neg_prio, eid = heapq.heappop(self._heap)
        ev = self._events.pop(eid, None)
        if ev:
            ev.cancelled = True
            self._remove_from_ordered(ev)
        return ev

    # ---------------------------------------------------------
    # 7. events_in_range(...)
    # ---------------------------------------------------------

    def events_in_range(self, start_ts: float, end_ts: float) -> List[Event]:
        """
        Return all events with timestamp in [start_ts, end_ts], ordered by timestamp.
        """
        result: List[Event] = []
        # find first index >= start_ts
        idx = bisect.bisect_left(self._ordered, (start_ts, ""))
        while idx < len(self._ordered):
            ts, eid = self._ordered[idx]
            if ts > end_ts:
                break
            ev = self._events.get(eid)
            if ev and not ev.cancelled:
                result.append(ev)
            idx += 1
        return result

    # ---------------------------------------------------------
    # 8. load_sample_data()
    # ---------------------------------------------------------

    def load_sample_data(self) -> None:
        """Load some sample events for testing/demo."""
        now = time.time()
        self.add_event("e1", "Morning standup", now + 300, 2, 900)
        self.add_event("e2", "Code review", now + 600, 3, 1800)
        self.add_event("e3", "Lunch break", now + 3600, 1, 3600)
        self.add_event("e4", "1:1 Meeting", now + 1800, 5, 1800)
        self.add_event("e5", "Deploy release", now + 7200, 4, 2700)


# ---------------------------------------------------------
# Simple demo when run as a script
# ---------------------------------------------------------

if __name__ == "__main__":
    sched = EventScheduler()
    sched.load_sample_data()

    print("All events loaded:")
    for eid, ev in sched._events.items():
        print(f"  {eid}: {ev}")

    print("\nNext event (peek):")
    print(sched.peek_next())

    print("\nEvents in next 2 hours:")
    now = time.time()
    for ev in sched.events_in_range(now, now + 7200):
        print(f"  {ev.event_id}: {ev.title} at {ev.timestamp}, prio={ev.priority}")

    print("\nPop next event:")
    print(sched.pop_next())

    print("\nNext event after pop:")
    print(sched.peek_next())
