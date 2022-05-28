
%experience(T,tute) :- previousTuteExperience(T,E), E > 0.
%experience(T,asst) :- previousAsstExperience(T,E), E > 0.

%capacity(T,tute,C) :- capacityTute(T,C).
%capacity(T,asst,C) :- capacityAsst(T,C).

role(tute). role(asst).
%class(S) :- day(S,D).

N { task(A,S,R) : teacher(A) } N :- class(S), role(R), requirement(R,N).

%:- task(A,S,tute), not experience(A,asst). % tutors need to have lab assistant experience
:- capacity(A,R,D), D+1 #count { S : task(A,S,R) }. % do not go beyond workload capacity

availabilityRequired(S,R,D,T+O..T+O+L-1) :- day(S,D), startTime(S,T), offset(R,O), duration(R,L).

:- task(A,S,R), availabilityRequired(S,R,D,T), mode(S,M), not available(A,M,D,T). % the teacher needs to be available online or in person at the right time.

intersect(S1,S2,R1,R2) :- availabilityRequired(S1,R1,D,T), availabilityRequired(S2,R2,D,T), S1 < S2.
%intersect(S1,S2,R1,R2) :- day(S1,D), day(S2,D), startTime(S1,T1), startTime(S2,T2), duration(R1,L1), offset(R1,O1), duration(R2,L2), offset(R2,O2), T1 + O1 + L1 >= T2, T2 + O2 + L2 >= T1, S1 < S2.
:- task(A,S1,R1), task(A,S2,R2), intersect(S1,S2,R1,R2). % avoid conflicting schedules

badPair(S) :- task(A1,S,R1), task(A2,S,R2), not experience(A1,R1), not experience(A2,R2).
:- badPairsLimit(L), L+1 #count { S : badPair(S)}.

desireLevel(X) :- desire(A,X,D,T).
individualSatisfactionBounded(A,S,R,X) :- task(A,S,R), desire(A,X,D,T), availabilityRequired(S,R,D,T).
satisfactionWorseThan(A,S,R,Y) :- individualSatisfactionBounded(A,S,R,X), individualSatisfactionBounded(A,S,R,Y), lessDesired(X,Y).
satisfaction(A,S,R,X) :- individualSatisfactionBounded(A,S,R,X), not satisfactionWorseThan(A,S,R,X).
satisfactionAggregate(X,C) :- desireLevel(X), C = #count { A,S,R : satisfaction(A,S,R,X) }.

:- satisfactionAggregate(X,C), upperSatisfactionBound(X,CT), C > CT.

strange(A,S,R) :- satisfaction(A,S,R,X1), satisfaction(A,S,R,X2), X1 != X2.

#show.
%#show hello/6.
#show task/3.
#show satisfactionAggregate/2.
%#show availabilityRequired/4.
#show strange/3.
