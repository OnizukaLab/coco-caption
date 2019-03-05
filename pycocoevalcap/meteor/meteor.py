#!/usr/bin/env python

# Python wrapper for METEOR implementation, by Xinlei Chen
# Acknowledge Michael Denkowski for the generous discussion and help 

import os
import sys
import subprocess
import threading

# Assumes meteor-1.5.jar is in the same directory as meteor.py.  Change as needed.
METEOR_JAR = 'meteor-1.5.jar'


class Meteor:

    def __init__(self):
        self.meteor_cmd = ['java', '-jar', '-Xmx2G', METEOR_JAR,
                           '-', '-', '-stdio', '-l', 'en', '-norm']
        # Used to guarantee thread safety
        self.lock = threading.Lock()
    
    def get_meteor_p(self):
        p = subprocess.Popen(self.meteor_cmd,
                             cwd=os.path.dirname(os.path.abspath(__file__)),
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             encoding="utf-8")
        return p

    def compute_score(self, gts, res):
        assert(list(gts.keys()) == list(res.keys()))
        imgIds = list(gts.keys())

        eval_line = 'EVAL'
        self.lock.acquire()
        for c, i in enumerate(imgIds):
            assert(len(res[i]) == 1)
            stat = self._stat(res[i][0], gts[i])
            eval_line += ' ||| {}'.format(stat)
            if c % 100 == 0:
                print("[{0}/{1}]".format(c, len(imgIds)))

        meteor_p = self.get_meteor_p()
        lines = meteor_p.communicate(input='{}\n'.format(eval_line), timeout=50)[0].split()
        scores = lines[:-1]
        scores = [float(e) for e in scores]
        score = float(lines[-1])
        self.lock.release()

        return score, scores

    def method(self):
        return "METEOR"

    def _stat(self, hypothesis_str, reference_list):
        # SCORE ||| reference 1 words ||| reference n words ||| hypothesis words
        hypothesis_str = hypothesis_str.replace('|||','').replace('  ',' ')
        score_line = ' ||| '.join(('SCORE', ' ||| '.join(reference_list), hypothesis_str))
        meteor_p = self.get_meteor_p()
        return meteor_p.communicate(input='{}\n'.format(score_line), timeout=15)[0].strip()

    def _score(self, hypothesis_str, reference_list):
        self.lock.acquire()
        # SCORE ||| reference 1 words ||| reference n words ||| hypothesis words
        hypothesis_str = hypothesis_str.replace('|||','').replace('  ',' ')
        score_line = ' ||| '.join(('SCORE', ' ||| '.join(reference_list), hypothesis_str))
        meteor_p = self.get_meteor_p()
        stats = meteor_p.communicate(input='{}\n'.format(score_line), timeout=15)[0].strip()
        eval_line = 'EVAL ||| {}'.format(stats)
        # EVAL ||| stats 

        score = self.get_meteor_p().communicate('{}\n'.format(eval_line), timeout=15)[0].strip()
        # score = float(meteor_p.stdout.readline().strip())
        # bug fix: there are two values returned by the jar file, one average, and one all, so do it twice
        # thanks for Andrej for pointing this out
        # score = float(meteor_p.stdout.readline().strip())
        self.lock.release()
        return score
