role(tute).
requirement(tute,1).
duration(tute,3).
offset(tute,0).

role(asst).
requirement(asst,1).
duration(asst,2).
offset(asst,1).

constraint(teamExperience(admin({COURSE_CODE})),none). % at least one person needs to have experience Y as admin in the team for a class. not a constraint here
constraint(roleExperience(tute,involved({COURSE_CODE})),soft(1)). % at least one person with role X needs to have experience in course Y for a class.
constraint(teamExperience(involved({COURSE_CODE})),soft(1)). % at least one person needs to have experience in course Y in the team for a class.
constraint(ubiquity,hard). % avoid conflicting schedules: we shouldn't assign multiple tasks with intersecting time range to the same person
constraint(roleCapacity,hard). % do not go beyond workload capacity
constraint(desire(1),soft(2)). % people shouldn't hate the times of the class allocated to them.
constraint(desire(2),soft(1)). % people should be enthousiastic about the times of the class allocated to them.
constraint(desire(3),none).    % 3 is the maximum desire level in our data, so no constraints here.
constraint(mode(inPerson),soft(5)). % an individual needs to actually be available in person at the right time to be assigned an in person class.
constraint(mode(online),soft(4)).   % an individual needs to actually be available online at the right time to be assigned an online class.
constraint(sufficientlyStaffed(asst),soft(3)). % a class needs to meet its quota of lab assistants
constraint(sufficientlyStaffed(tute),soft(3)). % a class needs to meet its quota of tutors
