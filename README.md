QuickEntry tool for Personal Kanban
========================

pkqe is a small tool to submit tasks to Personal Kanban via command line. The tool works in case PK is set up to use Redis server as data source.

To submit a task you invoke the script on command line:

pkqe.py <text of the new task with tags>
Possible tags:
* #tag - assign tag to the task
* @person - assign task to a specific person (search by Initials)
* %topic - set a specific topic on a task
* $column - assign column directly
* !! - set High priority (must precede the message)
* ! - set Medium priority (must precede the message)

Example:
`python pkqe.py !! Test task for a project $Pending %NewFeature #core #interface @DevA`

Will create a task with text "Test task for a project" on column "Pending", topic "NewFeature" and assign tags "core" and "interface". It will also set the assignee to person with initials DevA.

Python dependencies
========================
pkqe is written in Python and relies on the following modules:
* redis-py

Using with Launchy
========================
I use pkqe together with Launchy where a set a special tag for Runner plugin that launches the pkqe script.
