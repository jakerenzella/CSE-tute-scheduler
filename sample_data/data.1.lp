| Tutor Name    | Prev Term Tute Exp | Prev Term Tute Exp | Availability           | Capacity Tutorials | Capacity Assistant | Prefer Tutorial |
| ------------- | ------------------ | ------------------ | ---------------------- | ------------------ | ------------------ | --------------- |
| Jake Renzella | 2                  | 1                  | [0, 0, 1.1, 3.1, 3, 0] | 1                  | 1                  | Y               |

| Tutorial Name | Day | Time | Mode      |
| ------------- | --- | ---- | --------- |
| Mon1a         | Mon | 9:00 | Online    |
| Mon1b         | Mon | 9:00 | In Person |

teacher(jakeR).
previousTuteExperience(jakeR,2).
previousAsstExperience(jakeR,2).
preference(jakeR,mon,10,preferred).
availableInPerson(jakeR,mon,11,yes).
capacityTute(jakeR,1).
capacityAsst(jakeR,1).
preferTutorial(jakeR,yes).

slot(mon1a).
day(mon1a,mon).
startTime(mon1a,9).
mode(mon1a,online).

slot(mon1b).
day(mon1b,mon).
startTime(mon1b,9).
mode(mon1b,person).
