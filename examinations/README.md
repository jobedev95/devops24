# Examinations

In this directory you will find the examinations that make up the basis for
grading this course.

The examinations contains one or more questions that you answer as well as you
can. Refer to the manuals of each command, and try out the commands given (if any).
Remember you have a Vagrant environment, and can destroy and recreate the
environment as much as you want to get back to the initial condition.

The lettered QUESTIONS (A, B, C, etc.) are mandatory to attempt to solve for
each examination. The BONUS QUESTIONS are there for enlightenment, and if you
answer them, it will demonstrate a good understanding of the subject which plays
into the overall evaluation and grade.

The examination labs are evaluated on both established criteria and the overall
quality of the work. This is to make sure the grades are fair and reflect the
effort and understanding of each subject per the examinations.

It is suggested that you make a separate directory to keep your examinations in.
When you work in that directory, I recommend that you name the playbooks and
other artifacts so that it's obvious which examination they belong to.

You can then commit this directory to a git repo on GitHub and then provide the link,
or make a (compressed) tar or zip file of the whole directory and send me an email
with that file.

## Forking and Cloning This Repository

On GitHub you can make a fork of this repository and then clone your own copy onto
the computer you are working on.

You can then make the original repository an _upstream_ repo that you can use to
incorporate any fixes and changes.

You can do this by `cd` to the directory where your clone of _your own_ fork exists.
You can then make the original repo an upstream reference by doing

    $ git remote add upstream git@github.com:feinorgh/devops24.git

When you then run `git remote -v`, you should have two references:

    $ git remote -v
    origin  git@github.com:[your user]/devops24.git (fetch)
    origin  git@github.com:[your user]/devops24.git (push)
    upstream  git@github.com:feinorgh/devops24.git (fetch)
    upstream  git@github.com:feinorgh/devops24.git (push)

When you start working you can fetch any changes made in the `upstream` repo by doing

    $ git pull --ff-only upstream main

If you have made any changes in any of the files from upstream, you may need to `merge` the
changes by doing

    $ git merge upstream/main

If you get a merge conflict, refer to the git manual for how to resolve conflicts, or ask me
for help in class.

