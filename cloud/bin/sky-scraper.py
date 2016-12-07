#!/usr/bin/python

import sys
import getopt
import subprocess
import os
import scrapy
import psycopg2


def print_spiders():
    print("Available Spiders")
    print("================")
    subprocess.call(["scrapy", "list"])
    print("================")
    print("\n")
    exit(1)

def docky():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = dir_path + "/docker-compose.yml"
    print "Starting Docker Instance"
    print dir_path
    try:
        subprocess.check_output(["docker-compose", "-f", dir_path, "up", "-d"])
    except subprocess.CalledProcessError as e:
        print e.output

def killy():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    dir_path = dir_path + "/docker-compose.yml"
    print "Killing Docker Instance"
    print dir_path
    try:
        subprocess.check_output(["docker-compose", "-f", dir_path, "kill"])
    except subprocess.CalledProcessError as e:
        print e.output
    sys.exit(1)

def scrape_it(name):
    subprocess.call(["scrapy", "crawl", name])

def run_all_spiders():
    ps = subprocess.Popen(('scrapy', 'list'), stdout=subprocess.PIPE)
    output = subprocess.check_output(('xargs', '-n', '1', 'scrapy', 'crawl'), stdin=ps.stdout)
    ps.wait()

def access_database():
    try:
        subprocess.call(["psql", "-h", "localhost", "-p", "5432", "-U", "docker"])
    except subprocess.CalledProcessError as e:
        print e.output
    sys.exit(1)

def create_testdb():
    try:
        conn = psycopg2.connect("dbname='testdb' user='docker' host='localhost' password='docker'")
        print "testdb already exists..."
        conn.close()
        exit(1)
    except Exception as e:
        print "testdb database does not exist. Creating testdb..."
    try:
        conn = psycopg2.connect("dbname='docker' user='docker' host='localhost' password='docker'")
        print "connection succcessful"
    except Exception as e:
        print e
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    try:
        cur.execute("""CREATE DATABASE testdb""")
    except Exception as e:
        print "cannot create database"
        print e

def print_help():
    print "Sky-Scraper: For all of your cloud scraping needs!"
    print "usage: sky-scraper -n <spider-name>"
    print "     -n | --name=    spider name input"
    print "     -a              runs all available spiders"
    print "     -h              help"
    print "     -d              start docker splash/psql instances"
    print "     -k              kill docker splash/psql instances"
    print "     -l              list all available spiders"
    print "     -p              access psql database using docker credentials"
    print "     -c              create testdb if it does not exist"

def main(argv):

    spider_name = ''

    try:
        opts, args = getopt.getopt(argv, "hn:pcadkl", ["name="])
    except getopt.GetoptError:
        print_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print_help()
            sys.exit()
        elif opt in ("-n", "--name"):
            spider_name = arg
            print spider_name
            scrape_it(spider_name)
        elif opt == '-d':
            docky()
        elif opt == '-k':
            killy()
        elif opt == '-a':
            run_all_spiders()
        elif opt == '-l':
            print_spiders()
        elif opt == '-p':
            access_database()
        elif opt == '-c':
            create_testdb()
        else:
            print_help()
            sys.exit(2)

if __name__ == "__main__":
    if sys.argv[1:]:
        main(sys.argv[1:])
    else:
        print_help()


