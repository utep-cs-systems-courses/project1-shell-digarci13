#!/usr/bin/env python3


import os
import sys
import re


while 1:
    if 'PS1' in os.environ:
        os.write(1, (os.environ['PS1']).encode())
    else:
        os.write(1, ("$ ").encode())
        prompt = input()

    if prompt == 'exit':
        break

    cm = prompt.split()
    #Changes directory
    if cm[0] == 'cd':
        #removes cd from str
        nextDict = cm[1]
        try:
            os.chdir(nextDict)
        except:
            print("unable to change to directory")

    if 'ls' in prompt:
        path = os.getcwd()
        files = os.listdir(path)
        for x in files:
            print(x)
            
    pid = os.getpid()
    # os.write(1, ("About to fork (pid:%d)\n" % pid).encode())
    rc = os.fork()
    if rc < 0:
        # os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    elif rc == 0:  # child

        # os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" %(os.getpid(), pid)).encode())
        args = prompt.split()

    if "<" in prompt:  # redirect in
        os.close(0)  # Redirect input
        sys.stdin = open(prompt[1].strip(), 'r')  # open and set to read
        os.set_inheritable(0, True)
        path(prompt[0].split())

    if ">" in prompt:  # redirect out
        os.close(1)
        sys.stdout = open(prompt[1].strip(), "w")  # open and set to write
        os.set_inheritable(1, True)
        path(prompt[0].split())


    if '|' in prompt:
        pipe = prompt.split("|")
        p1 = pipe[0].split()
        p2 = pipe[1].split()

        r, w = os.pipe()  # file descriptors pr, pw for reading and writing
        for f in (r, w):
            os.set_inheritable(f, True)
        print("pipe fds: pr=%d, pw=%d" % (pr, pw))
        print("About to fork (pid=%d)" % pid)
        pipeFork = os.fork()
        if pipeFork < 0:  # fork failed
            print("fork failed, returning %d\n" % rc, file=sys.stderr)
            # os.write(2, ('Fork failed').encode())
            sys.exit(1)

        if pipeFork == 0:  # child - will write to pipe
            print("Child: My pid==%d.  Parent's pid=%d" % (os.getpid(), pid), file=sys.stderr)
            args = ["wc", "p3-exec.py"]
            os.close(1)  # redirect child's stdout
            os.dup(w)
            os.set_inheritable(1, True)

            for fd in (r, w):
                os.close(fd)
            path(p1)
        else:  # parent (forked ok)
            print("Parent: My pid==%d.  Child's pid=%d" % (os.getpid(), rc), file=sys.stderr)
            os.close(0)
            os.dup(r)
            os.set_inheritable(0, True)
            for fd in (w, r):
                os.close(fd)
            path(p2)



