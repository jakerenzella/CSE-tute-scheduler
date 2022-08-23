availabilityRequired(SLOT,ROLE,DAY,TIME+OFFSET..TIME+OFFSET+LENGTH-1) :- day(SLOT,DAY), startTime(SLOT,TIME), offset(ROLE,OFFSET), duration(ROLE,LENGTH).
intersect(SLOT1,SLOT2,ROLE1,ROLE2) :- availabilityRequired(SLOT1,ROLE1,DAY,TIME), availabilityRequired(SLOT2,ROLE2,DAY,TIME), SLOT1 < SLOT2.
intersect(SLOT,SLOT,ROLE1,ROLE2)   :- availabilityRequired(SLOT ,ROLE1,DAY,TIME), availabilityRequired(SLOT ,ROLE2,DAY,TIME), ROLE1 < ROLE2.

{ assign(A,SLOT,ROLE) : teacher(A) } NEEDED :- class(SLOT), role(ROLE), requirement(ROLE,NEEDED).

badSign(sufficientlyStaffed(ROLE),SLOT,NEEDED-ASSIGNED) :- class(SLOT), requirement(ROLE,NEEDED), ASSIGNED = #count { A : assign(A,SLOT,ROLE) }, NEEDED > ASSIGNED.

%badSign(roleCapacity,A,B-D) :- capacity(A,R,D), B = #count { S : assign(A,S,R) }, B > D.
badSign(roleCapacity,A,1) :- capacity(A,ROLE,BOUND), BOUND+1 = #count { SLOT : assign(A,SLOT,ROLE) }.

badSign(mode(MODE),task(SLOT),1) :- assign(A,SLOT,ROLE), availabilityRequired(SLOT,ROLE,DAY,TIME), mode(SLOT,MODE), not available(A,MODE,DAY,TIME).

badSign(ubiquity,overlap(A,SLOT1,ROLE1,SLOT2,ROLE2),1) :- assign(A,SLOT1,ROLE1), assign(A,SLOT2,ROLE2), intersect(SLOT1,SLOT2,ROLE1,ROLE2).

roleExperienceCovered(SLOT,ROLE,SKILL) :- assign(A,SLOT,ROLE), experience(A,SKILL).
badSign(roleExperience(ROLE,SKILL),SLOT,1) :- class(SLOT), role(ROLE), constraint(roleExperience(ROLE,SKILL),TYPE), not roleExperienceCovered(SLOT,ROLE,SKILL).

teamExperienceCovered(SLOT,SKILL) :- assign(A,SLOT,ROLE), experience(A,SKILL).
badSign(teamExperience(SKILL),SLOT,1) :- class(SLOT), constraint(teamExperience(SKILL),TYPE), not teamExperienceCovered(SLOT,SKILL).

taskTimeSatisfaction(A,SLOT,ROLE,LEVEL) :- assign(A,SLOT,ROLE), LEVEL = #min { INTENSITY : desire(A,INTENSITY,DAY,TIME), availabilityRequired(SLOT,ROLE,DAY,TIME) }.
badSign(desire(LEVEL),task(A,SLOT,ROLE),1) :- taskTimeSatisfaction(A,SLOT,ROLE,LEVEL).

constrained(CONSTRAINT) :- constraint(CONSTRAINT,TYPE), TYPE != none.
unconstrained(CONSTRAINT) :- badSign(CONSTRAINT,A,WEIGHT), not constrained(CONSTRAINT), not constraint(CONSTRAINT,none).
bad(CONSTRAINT,A) :- badSign(CONSTRAINT,A,WEIGHT), constrained(CONSTRAINT).

badnessAggregate(CONSTRAINT,COUNT) :- constraint(CONSTRAINT,soft(PRIORITY)), COUNT = #sum { WEIGHT,A : badSign(CONSTRAINT,A,WEIGHT) }.

constraint(CONSTRAINT,hardBound(0)) :- constraint(CONSTRAINT,hard).
:- constraint(CONSTRAINT,hardBound(BOUND)), BOUND+1 #sum { WEIGHT,A : badSign(CONSTRAINT,A,WEIGHT) }.
#minimize { COUNT@PRIORITY : constraint(CONSTRAINT,soft(PRIORITY)), badnessAggregate(CONSTRAINT,COUNT) }.

#show.
#show assign/3.
#show badnessAggregate/2.
#show bad/2.
