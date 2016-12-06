#!/usr/bin/sh

import sys
import getopt
import subprocess
import os

def main(argv):

    spider_name = ''
    start_docker = False
    kill_docker = False
    all_spiders = False

    try:
        opts, args = getopt.getopt(argv, "hn:dk", ["name="])
    except getopt.GetoptError:
        print 'sky-scraper -n <spider-name>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print "Sky-Scraper: For all of your cloud scraping needs!"
            print "usage: sky-scraper -n <spider-name>"
            print "     -n | --name=    spider name input"
            print "     -all            runs all available spiders"
            print "     -h              help"
            print "     -d              start docker splash/psql instances"
            print "     -k              kill docker splash/psql instances"
            sys.exit()
        elif opt in ("-n", "--name"):
            spider_name = arg
            print spider_name
        elif opt in ("-d"):
            start_docker = True
        elif opt in ("-k"):
            kill_docker = True
        elif opt in ("-all"):
            all_spiders = True
        else:
            print 'sky-scraper -n <spider-name>'
            sys.exit(2)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = dir_path + "/docker-compose.yml"

    if start_docker:
        print "Starting Docker Instance"
        print dir_path
        try:
            subprocess.check_output(["docker-compose", "-f", dir_path, "up", "-d"])
        except subprocess.CalledProcessError as e:
            print e.output

    if kill_docker:
        print "Killing Docker Instance"
        print dir_path
        try:
            subprocess.check_output(["docker-compose", "-f", dir_path, "kill"])
        except subprocess.CalledProcessError as e:
            print e.output
        sys.exit(1)
    

if __name__ == "__main__":
    if sys.argv[1:]:
        main(sys.argv[1:])
    else:
        print "usage: sky-scraper -n <spider-name>"