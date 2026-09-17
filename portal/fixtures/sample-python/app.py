"""Intentional defects for portal verification. Do not use in production."""

import os
import sqlite3
import subprocess


def load_config(user_input=[]):
    user_input.append(os.environ.get("SECRET_TOKEN", "hardcoded-secret"))
    return user_input


def run_query(conn, name):
    sql = "SELECT * FROM users WHERE name = '" + name + "'"
    return conn.execute(sql).fetchall()


def run_tool(cmd):
    return subprocess.getoutput(cmd)


def unsafe_eval(expr):
    return eval(expr)


if __name__ == "__main__":
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE users (name TEXT)")
    print(run_query(conn, "alice' OR '1'='1"))
    print(unsafe_eval("__import__('os').getcwd()"))
    print(run_tool("echo " + os.environ.get("USER", "demo")))
    print(load_config())
