#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

class DBHelper:
    def __init__(self, dbname="todo.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False, timeout=5)

    def setup(self):
        stmt = '''
        CREATE TABLE IF NOT EXISTS dict (
        	id integer primary key autoincrement, 
        	french text, 
        	english text);
        CREATE TABLE IF NOT EXISTS subscriptions (user_name, news_source);
               '''
        self.conn.executescript(stmt)
        self.conn.commit()

    def add_item(self, french, english):
        stmt = "INSERT INTO dict (french, english) VALUES (?,?)"
        args = (french, english)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_item(self, french):
        stmt = "DELETE FROM dict WHERE french = (?)"
        args = french
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_dict(self):
        stmt = "SELECT french, english FROM dict"
        return [(x[0],x[1]) for x in self.conn.execute(stmt)]
    
    def get_french(self, english):
    		stmt = "SELECT french FROM dict WHERE english = (?)"
    		args = (english,)
    		return [x[0] for x in self.conn.execute(stmt, args)]
    
    def get_english(self, french):
    		stmt = "SELECT english FROM dict WHERE french = (?)"
    		args = (french,)
    		return [x[0] for x in self.conn.execute(stmt, args)]
    		
    def get_dict_entry(self, id):
        stmt = "SELECT french, english FROM dict WHERE id = (?)"
        args = (id,)
        return self.conn.execute(stmt,args).fetchone()
    
    def get_dict_entry_count(self):
    		stmt = "SELECT count(*) FROM dict"
    		return self.conn.execute(stmt).fetchone()[0]
    		

    def add_subscription(self, user_name, news_source):
        stmt = "INSERT INTO subscriptions (user_name, news_source) VALUES (?, ?)"
        args = (user_name, news_source)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_subscription(self, user_name, news_source):
        stmt = "DELETE FROM subscriptions WHERE user_name = (?) AND news_source = (?)"
        args = (user_name, news_source)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_subscriptions(self, user_name):
        """ Gives an array of news_source """
        stmt = "SELECT news_source FROM subscriptions"
        return [ x[0] for x in self.conn.execute(stmt)]
