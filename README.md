# assistant_bot
Assistant bot for teachers to manage the studying process in telegram chat

# quick start

**/help** -- displays main features of the bot

**/start** -- the one who starts the bot is considered a teacher and has higher privileges 

**/stop** -- only teacher can stop the bot

**/present name1 name2** -- will increase the presence count for listed students by one.

Name1 1

Name2 3

**/grade +- name1 name2** -- rule's 1st argument is an option + (for prepared students) or - (for unprepared students)

Name1 ++

Name2

Name3 -

**/random** -- saves you the trouble of choosing who will go to the blackboard

Name2

**/ignore name0** -- specified users are no longer considered students

**/register** -- every student presses this button

student name0 registered

**/timer N** -- sets the timer for N minutes

Timer set for 5 minutes

…

Times up!

# configuration

## environment variables

BOT_TOKEN -- your telegram bot token