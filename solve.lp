
duration(tute,3).
duration(asst,2).
offset(tute,0).
offset(asst,1).
badPairsLimit(5).

experience(T,tute) :- previousTuteExperience(T,E), E > 0.
experience(T,asst) :- previousAsstExperience(T,E), E > 0.

capacity(T,tute,C) :- capacityTute(T,C).
capacity(T,asst,C) :- capacityAsst(T,C).

role(tute). role(asst).
slot(S) :- day(S,D).

1 { task(T,R,S) : teacher(T) } 1 :- slot(S), role(R).

:- task(T,tute,S), not experience(T,asst).
:- C = #count { S : task(T,R,S) }, C > D, capacity(T,R,D).


intersect(S1,S2,R1,R2) :- day(S1,D), day(S2,D), startTime(S1,T1), startTime(S2,T2), duration(R1,D1), offset(R1,O1), duration(R2,D2), offset(R2,O2), T1 + O1 + D1 >= T2, T2 + O2 + D2 >= T1, S1 < S2.
:- task(T,R1,S1), task(T,R2,S2), intersect(T,S1,S2,R1,R2).

badPair(S) :- task(T1,R1,S), task(T2,R2,S), not experience(T1,R1), not experience(T2,R2).
:- C = #count { S : badPair(S)}, badPairsLimit(L), C > L .

