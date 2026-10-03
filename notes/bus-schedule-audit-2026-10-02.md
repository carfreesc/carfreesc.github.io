# State College intercity bus audit — October 2, 2026

This is the research note behind the revised `gettinghere.md` bus tables for carfreesc.github.io.

## What I counted

The goal is to count **physical, one-seat buses through State College**, not every itinerary sold by a booking engine. This matters because Greyhound/FlixBus/Wanderu/Omio can sell a destination itinerary that begins on one physical bus and then transfers. The clearest example in the current inventory is the 1:50 PM Greyhound departure from State College: it is a direct bus to Philadelphia, but tickets are also sold from State College to New York beginning on that bus and requiring a transfer.

Audit window: **Friday, October 2 through Thursday, October 8, 2026**. The tables in the site encode recurring weekday patterns visible in the current fall inventory, with Fullington checked against its own published/live schedules.

Primary sources used:

- Fullington live booking pages: https://ride.fullingtontours.com/
- Fullington published daily departures: https://www.fullingtontours.com/daily-bus-departures/
- Fullington 2026 express schedules: https://www.fullingtontours.com/express-bus-service/
- Greyhound route/station pages: https://www.greyhound.com/
- Wanderu current-week inventory: https://www.wanderu.com/
- Omio operator/time/day-of-week timetable pages: https://www.omio.com/
- GotoBus/Agee current booking calendar: https://www.gotobus.com/
- OurBus route and live-availability pages: https://www.ourbus.com/

## Regular one-seat departures from State College

| Departure | Operator | Through destination | Arrival | Runs in audited pattern | State College stop / notes |
| --- | --- | --- | --- | --- | --- |
| 1:55 AM | FlixBus | New York | 6:30 AM | M Tu W F Sa Su | SCE |
| 6:00 AM | Fullington | Pittsburgh / PIT | 11:00 AM / 11:40 AM | Daily | Downtown |
| 9:00 AM | Fullington | New York | 1:45 PM | Daily | Downtown; Area X in New York |
| 9:15 AM | Fullington | Philadelphia | 1:45 PM | Daily | Downtown; Harrisburg 11:00, KOP 1:00 |
| 9:45 AM | Fullington | Wilkes-Barre | 1:10 PM | Daily | Downtown; Lock Haven/Williamsport |
| 10:25 AM | FlixBus | New York | 4:25 PM | M Tu Th F Sa Su | SCE; Harrisburg 12:10 |
| 12:35 PM | Greyhound | New York | 6:45 PM | M Th F Sa Su | Downtown; Harrisburg about 2:20 |
| 1:25 PM | Greyhound | Pittsburgh | 6:10 PM | W Th F Sa Su | Downtown; pattern is schedule-sensitive |
| 1:50 PM | Greyhound | Philadelphia | 6:15 PM | Daily | Downtown; Harrisburg 3:40; direct PHL, **not** direct NYC |
| 3:40 PM | FlixBus | New York | 10:20 PM | M Tu F Sa Su | SCE; Harrisburg 5:25, Philadelphia 8:15 |
| 4:25 PM | FlixBus | Pittsburgh | 7:25 PM | W Th F Sa Su | SCE; schedule-sensitive |
| 6:25 PM | Greyhound | Pittsburgh | 11:10 PM | M Tu | Downtown; schedule-sensitive |
| 6:55 PM | FlixBus | Pittsburgh | 9:30 PM | Th F Sa Su | SCE; schedule-sensitive |
| 7:20 PM | Fullington | Pittsburgh | 9:50 PM | Daily | Downtown |
| 7:35 PM | Greyhound | Pittsburgh | 10:20 PM | W Th F Sa Su | Downtown; schedule-sensitive |
| 8:25 PM | FlixBus | Pittsburgh | 11:25 PM | M Tu | SCE; schedule-sensitive |

The Pittsburgh Greyhound/FlixBus slots are the least stable portion of the table. Current and recently crawled booking inventories show late-evening variants shifting among weekdays, so the site deliberately warns readers to check the live calendar rather than treating these as permanent timetable slots.

## Regular one-seat arrivals in State College

| Arrival | Operator | Through origin | Departure | Runs in audited pattern | State College stop / notes |
| --- | --- | --- | --- | --- | --- |
| 1:50 AM | FlixBus | New York | 9:30 PM | M W Th F Sa Su | SCE; next-day arrival |
| 8:45 AM | Fullington | Pittsburgh | 6:15 AM | Daily | Downtown; continues toward New York |
| 10:20 AM | FlixBus | Pittsburgh | 7:30 AM | M Tu Th F Sa Su | SCE |
| 12:20 PM | Greyhound | Pittsburgh | 9:35 AM | M Th F Sa Su | Downtown |
| 1:15 PM | Greyhound | Philadelphia | 9:00 AM | Daily | Downtown; Harrisburg about 11:25 |
| 1:40 PM | Greyhound | Pittsburgh | 9:10 AM | Daily | Downtown |
| 3:35 PM | FlixBus | Pittsburgh | 1:00 PM | M Tu F Sa Su | SCE |
| 4:20 PM | FlixBus | New York | 10:45 AM | M W Th F Sa Su | SCE |
| 5:15 PM | Fullington | Wilkes-Barre | 1:36 PM | Daily | Downtown; SCE stop at 4:55 |
| 6:30 PM | Fullington | Philadelphia | 2:00 PM | Daily | Downtown |
| 6:50 PM | FlixBus | New York | 12:00 PM | M Th F Sa Su | SCE; via Philadelphia |
| 7:05 PM | Fullington | New York | 2:05 PM | Daily | Downtown; official daily FAB202 |
| 7:20 PM | Greyhound | New York | 1:00 PM | W Th F Sa Su | Downtown |
| 8:10 PM | Fullington | Pittsburgh / PIT | 3:30 PM / 2:50 PM | Daily | Downtown; continues to SCE at 8:20 |

### Fullington duplicate/extra inventory note

Fullington's live ticketing backend showed **two** 2:05 PM New York departures on October 2: FAB202 arriving State College at 7:05 PM and FAB211 (via Rockaway and East Stroudsburg) arriving at 6:45 PM. Fullington's published *Daily Bus Departures* page lists FAB202 as the daily New York–State College–Pittsburgh service, so the site table treats 7:05 PM as the regular daily arrival and leaves FAB211 out of the permanent table. It is worth watching this if maintaining the schedule.

## Date-dependent services

- **Agee:** GotoBus showed service only on selected dates in the audited week. A current 7:30 AM State College run serves EWR about 11:00 AM, Newark city about 11:10, New York about 11:30, and LGA about 12:15; a common New York return is 5:00 PM–9:25 PM. The calendar is too variable for a weekday-pattern table.
- **OurBus:** the operator's route pages advertise a 2:30 PM State College departure to New York and Philadelphia, but its live State College–Harrisburg calendar showed the 2:30–4:15 trip on Friday October 2 and not the surrounding weekdays. The site therefore says **selected dates** rather than “daily.”
- **Fullington Big Apple Express:** the 2026 published express timetable has State College 4:15 PM → New York 9:15 PM and New York 10:00 PM → State College 2:45 AM. Live inventory showed the outbound trip on a subset of the audited week, so it is treated as selected-date express service, not daily service.

## Key corrections found by the audit

1. The **1:50 PM Greyhound is a direct Philadelphia bus**, not a second direct New York bus. New York tickets beginning on it require a transfer.
2. Greyhound/FlixBus headline claims like “5 trips daily” can include the other brand, partner carriers, and connecting itineraries. They should not be used as physical-bus counts.
3. The directly audited FlixBus-operated State College trips use **SCE**. The Flix/Greyhound sales platform also offers partner itineraries from the downtown terminal.
4. The Newark stop on the audited Flix New York service is **Newark Penn Station**, not Newark Liberty Airport. Agee is the directly verified selected-date EWR service.
5. Pittsburgh is the least stable corridor by weekday; its Greyhound/FlixBus departure slots should be re-audited whenever the page is refreshed.

## Confidence

- Fullington daily core routes: **high** (operator-published schedule plus current live inventory).
- Daily direct Greyhound Philadelphia pair: **high** (current seven-day inventory and direct-trip listings).
- Greyhound/FlixBus New York weekday patterns: **moderately high**, but seasonal inventory can change.
- Greyhound/FlixBus Pittsburgh weekday patterns: **moderate**; specifically flagged on the site as schedule-sensitive.
- Agee/OurBus selected-date service: **high that the services exist; low that any fixed weekday pattern will persist**, hence no fixed weekday pattern is claimed.
