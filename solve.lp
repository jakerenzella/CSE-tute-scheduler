
N { task(A,S,R) : teacher(A) } N :- class(S), role(R), requirement(R,N).

:- task(A,S,tute), not experience(A,asst). % tutors need to have lab assistant experience
% make this a soft constraint (minimize)?

:- capacity(A,R,D), D+1 #count { S : task(A,S,R) }. % do not go beyond workload capacity

availabilityRequired(S,R,D,T+O..T+O+L-1) :- day(S,D), startTime(S,T), offset(R,O), duration(R,L).

badMode(A,S,M) :- task(A,S,R), availabilityRequired(S,R,D,T), mode(S,M), not available(A,M,D,T). % the teacher needs to be available online or in person at the right time.
%:- badMode(A,S,M).

intersect(S1,S2,R1,R2) :- availabilityRequired(S1,R1,D,T), availabilityRequired(S2,R2,D,T), S1 < S2.
intersect(S,S,R1,R2)   :- availabilityRequired(S ,R1,D,T), availabilityRequired(S ,R2,D,T), R1 < R2.
:- task(A,S1,R1), task(A,S2,R2), intersect(S1,S2,R1,R2). % avoid conflicting schedules

badPair(S) :- task(A1,S,R1), task(A2,S,R2), not experience(A1,R1), not experience(A2,R2).
:- badPairsLimit(L), L+1 #count { S : badPair(S)}. % try to avoid two people inexperienced people in class

individualSatisfactionBounded(A,S,R,X) :- task(A,S,R), desire(A,X,D,T), availabilityRequired(S,R,D,T).
satisfactionWorseThan(A,S,R,Y) :- individualSatisfactionBounded(A,S,R,X), individualSatisfactionBounded(A,S,R,Y), lessDesired(X,Y).
satisfaction(A,S,R,X) :- individualSatisfactionBounded(A,S,R,X), not satisfactionWorseThan(A,S,R,X).
satisfactionAggregate(X,C) :- desireLevel(X), C = #count { A,S,R : satisfaction(A,S,R,X) }.

% higher priority number is higher priority
#minimize { 1@4,S : badMode(A,S,inPerson) }.
#minimize { 1@3,S : badMode(A,S,online) }.
#minimize { 1@2,A,S : satisfaction(A,S,R,dislike) }.
#minimize { 1@1,A,S : satisfaction(A,S,R,possible) }.

#show.
#show task/3.
#show satisfactionAggregate/2.
%#show badMode/3.
#show needMoreAvail(S) : badMode(A,S,M). %We need more tutors to be available for these times
#show disatisfied(A,S,R) : satisfaction(A,S,R,X), X != preferred.
%#show inexp(A,S) : task(A,S,tute), not experience(A,asst).