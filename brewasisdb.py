# "Database code"

import os
import psycopg2

DATABASE_URL = 'brewasis'

def get_data(query):
  """Return data from the database."""
  db = psycopg2.connect('postgresql://localhost/brewasis', user='postgres', password='password')
  c = db.cursor()
  c.execute(query)
  return c.fetchall()
  db.close()

def add_craft(company, state, barrels2008, barrels2009, barrels2010, barrels2011, barrels2012, barrels2013, barrels2014, barrels2015, barrels2016, barrels2017, barrels2018):
  db = psycopg2.connect('postgresql://localhost/brewasis', user='postgres', password='password')
  c = db.cursor()
  c.execute("insert into craft values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (company, state, barrels2008, barrels2009, barrels2010, barrels2011, barrels2012, barrels2013, barrels2014, barrels2015, barrels2016, barrels2017, barrels2018))
  db.commit()
  db.close()

def add_companies(company, state):
  db = psycopg2.connect('postgresql://localhost/brewasis', user='postgres', password='password')
  c = db.cursor()
  c.execute("insert into companies values (default, %s, %s)", (company, state))
  db.commit()
  db.close()

def add_salary(size, principal, brewmaster, mngr, head, assistant, cellar, packmngr, canner, other):
  db = psycopg2.connect('postgresql://localhost/brewasis', user='postgres', password='password')
  c = db.cursor()
  c.execute("insert into salary values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (size, principal, brewmaster, mngr, head, assistant, cellar, packmngr, canner, other))
  db.commit()
  db.close()

def if_exist(table_name):
  db = psycopg2.connect('postgresql://localhost/brewasis', user='postgres', password='password')
  c = db.cursor()
  c.execute("select exists (select * from %s)" % table_name)
  return c.fetchall()
  db.close()

def add_brew2018(state, produced, population, num_co, rank, by_adults, capita):
  db = psycopg2.connect('postgresql://localhost/brewasis', user='postgres', password='password')
  c = db.cursor()
  c.execute("insert into brew2018 values (%s, %s, %s, %s, %s, %s, %s)", (state, produced, population, num_co, rank, by_adults, capita))
  db.commit()
  db.close()

def add_brew2011_2018(state, prod2011, prod2012, prod2013, prod2014, prod2015, prod2016, prod2017, prod2018):
  db = psycopg2.connect('postgresql://localhost/brewasis', user='postgres', password='password')
  c = db.cursor()
  c.execute("insert into brew2011_2018 values (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (state, prod2011, prod2012, prod2013, prod2014, prod2015, prod2016, prod2017, prod2018))
  db.commit()
  db.close()

def add_population(state, pop, percent, adults):
  db = psycopg2.connect('postgresql://localhost/brewasis', user='postgres', password='password')
  c = db.cursor()
  c.execute("insert into population values (%s, %s, %s, %s)", (state, pop, percent, adults))
  db.commit()
  db.close()
