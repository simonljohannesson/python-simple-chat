# python-simple-chat
## Introduction
This is a little project I've been working on to have
something to do and as a way to get back into coding
with Python. 

It's simple chat scripts written in Python, that uses
client-server communication and stores data in SQLite
databases for both client and server.
## Scope
The focus of the project has been to gain a better
understanding of some Python modules and becoming
more comfortable using Python in general since it is
the language that I write most of my personal automation
scripts in. Rather than create an application that will
actually provide value it was seen as a learning
experience. Security was not in the scope of this project.

The modules and concepts I was interested in when starting
the project were:
- The Python module socket
- Experimenting with persistent data storage, like SQLite
- Light usage of Python multithreading
- Trying to manage a project that's a bit bigger than I'm
used to

## Lessons learned
During the project I picked up on a few things that I feel
like I want to remember, and so I'm writing them down here.
1. Plan ahead
    - Choosing a good structure for the project files
    before writing any code will help with organization.
    - Time spent on planning the design will be worth it,
    this project I didn't spend enough time.
    - Spend time on deciding what abstractions make
    sense to make sure the project turn out/stay consistent
    during its lifetime.
    - Spend more time when choosing names for functions,
    classes, methods etc. It greatly helps with readability,
    and makes many comments redundant.
1. Start with the documentation
    - Writing the documentation for a function or method
    before implementing it will make sure the behaviour
    of it is already defined.
1. Don't stress through the project
    - Take the time to research the modules / technologies
    that are used in the project. It's a great opportunity
     to learn, and it will help avoid incorrect usages.
    - See point 1. Take the time.
1. Write tests.
    - Write tests and write them right away. It ties in well
    with not stressing, starting with the documentation
    and planning ahead. Because if the design is sound and
    the behavior of the code is well defined the code is
    less likely to be refactored to the point that the 
    tests are useless and the time will have been worth it.

## Practical notes on the project
- There are two almost identical client scripts present in
in the project, they point to two different locations where
they can store their respective database. If starting two
clients with connections to the same database the project
will not work properly so that's why there are two. Usually
only one script would run per computer.
- In order to work the client's database path need to be valid.
There is no need for a database to be present but if the
directory is not present then there will be errors.