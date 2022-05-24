# Problem Description

## Definitions

- **Tute/lab** - a 1 hour tutorial followed by a 2 hour lab, these are contiguous (scheduled as 3 hour blocks)
  - Can be online or in person.
- **Tutor** - the primary tute/lab teacher, will be present for the entire 3 hours of a tute/lab. Usually more experienced than the lab assistant, as they must have previous experience lab assisting or tutoring in the course.
- **Lab Assistant** - only present for the 2 hour lab (the last two hours of the tute/lab). Usually less experienced than the tutor. Can be a first time teacher.
- **Availability Key** (for a particular time):
  - impossible 0
  - dislike 1.1
  - dislike-online-only 1
  - possible 2.1
  - possible-online-only 2
  - preferred 3.1
  - preferred-online-only 3
- **Capacity** (number of type they can take
  - Max Tutorial (integer)
  - Max Assistant (integer)

## Constraints

### Requirements

- A tutor must have experience as a lab assist in a previous term.

### Nice to have

- Ideally a first time tutor (so only experience lab assisting) will not be paired with a first time lab assistant.

## Example Input

| Tutor Name    | Prev Term Tute Exp | Prev Term Tute Exp | Availability           | Capacity Tutorials | Capacity Assistant | Prefer Tutorial |
| ------------- | ------------------ | ------------------ | ---------------------- | ------------------ | ------------------ | --------------- |
| Jake Renzella | 2                  | 1                  | [0, 0, 1.1, 3.1, 3, 0] | 1                  | 1                  | Y               |

| Tutorial Name | Day | Time | Mode      |
| ------------- | --- | ---- | --------- |
| Mon1a         | Mon | 9:00 | Online    |
| Mon1b         | Mon | 9:00 | In Person |

## Sample Data
* Tutorials: Should be straight-forwards
* preferences: I am not sure what the number exactly means... I will clarify. From CASTLE it comes back as either x.y where x is the availability and is either 0 = impossible, 1 = dislike, 2 = possible 3 = preferred. Also need to clarify how y works but I think it indicates if in person or online.
These scores are being manipulated before going into the spreadsheet - I will clarify what's happening.