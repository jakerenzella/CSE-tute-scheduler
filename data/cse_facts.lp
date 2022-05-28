%tuteLabDuration(3). %unused?
requirement(tute,1).
duration(tute,3).
offset(tute,0).

requirement(asst,1).
duration(asst,2).
offset(asst,1).

badPairsLimit(5).
upperSatisfactionBound(dislike,0).
upperSatisfactionBound(possible,1).
lessDesired(dislike,possible). lessDesired(dislike,preferred). lessDesired(possible,preferred).
