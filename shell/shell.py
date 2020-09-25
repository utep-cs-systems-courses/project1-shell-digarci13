#!/usr/bin/env python3


import os
import sys
import re


while 1:
    if 'PS1' in os.environ:
        os.write(1, (os.environ['PS1']).encode())
    else:
        os.write(1, ("$ ").encode())

    pid = os.getpid()
    rc = os.fork()

    prompt = input()


    if prompt == "":  # no input
        pass

    if 'exit' in prompt:
        break

    cm = prompt.split()

    #Changes directory
    if 'cd' in prompt:
        nextDict = ''
        if 'cd..' in prompt:
            nextDict = '..'
        else:
            # removes cd from str
            nextDict = cm[1]

        try:
            os.chdir(nextDict)
        except FileNotFoundError:
            pass


    if 'ls' in prompt:
        path = os.getcwd()
        files = os.listdir(path)
        for x in files:
            print(x)



    if "<" in prompt:  # redirect in
        os.close(0)  # Redirect input
        sys.stdin = open(cm[1].strip(), 'r')  # open and set to read
        os.set_inheritable(0, True)
        path(prompt[0].split())

    if ">" in prompt:  # redirect out
        os.close(1)
        sys.stdout = open(cm[1].strip(), "w")  # open and set to write
        os.set_inheritable(1, True)
        path(prompt[0].split())


    if '|' in prompt:
        pipe = prompt.split("|")
        p1 = pipe[0].split()
        p2 = pipe[1].split()

        pr, pw = os.pipe()  # file descriptors pr, pw for reading and writing
        for f in (pr, pw):
            os.set_inheritable(f, True)
        #print("pipe fds: pr=%d, pw=%d" % (pr, pw))
        #print("About to fork (pid=%d)" % pid)
        pipeFork = os.fork()
        if pipeFork < 0:  # fork failed
            #print("fork failed, returning %d\n" % rc, file=sys.stderr)
            # os.write(2, ('Fork failed').encode())
            sys.exit(1)

        if pipeFork == 0:  # child - will write to pipe
            #print("Child: My pid==%d.  Parent's pid=%d" % (os.getpid(), pid), file=sys.stderr)
            #args = ["wc", "p3-exec.py"]
            os.close(1)  # redirect child's stdout
            os.dup(pw)
            os.set_inheritable(1, True)

            for fd in (pr, pw):
                os.close(fd)
            path(p1)
        else:  # parent (forked ok)
            #print("Parent: My pid==%d.  Child's pid=%d" % (os.getpid(), rc), file=sys.stderr)
            os.close(0)
            os.dup(pr)
            os.set_inheritable(0, True)
            for fd in (pw, pr):
                os.close(fd)
            path(p2)



    else:
        args = prompt.split()

        for dir in re.split(":", os.environ['PATH']):  # try each directory in the path
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ)  # try to exec program
            except FileNotFoundError:  # ...expected
                pass  # ...fail quietly

        os.write(2, ("Could not excecute the following command \"%s\"\n" % prompt).encode())
        sys.exit(1)  # terminate with error if execve could not run program




