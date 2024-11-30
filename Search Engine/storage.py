import sqlite3
import pandas as pd

class DBStorage():
    def __init__(self):
        self.con = sqlite3.connect('links.db')
        self.setup_tables()

    def setup_tables(self):
        cur = self.con.cursor()
        results_table = r"""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY,
                query TEXT,
                rank INTEGER,
                link TEXT,
                title TEXT,
                snippet TEXT,
                html TEXT,
                created DATETIME,
                relevance INTEGER,
                UNIQUE(query, link)
            );
            """
        cur.execute(results_table)
        self.con.commit()
        cur.close()

    def query_results(self, query):
        df = pd.read_sql(f"select * from results where query='{query}' order by rank asc", self.con)
        return df

    def insert_row(self, values):
        cur = self.con.cursor()
        try:
            cur.execute('INSERT INTO results (query, rank, link, title, snippet, html, created) VALUES(?, ?, ?, ?, ?, ?, ?)', values)
            self.con.commit()
        except sqlite3.IntegrityError:
            pass
        cur.close()

    def update_relevance(self, query, link, relevance):
        cur = self.con.cursor()
        cur.execute('UPDATE results SET relevance=? WHERE query=? AND link=?', [relevance, query, link])
        self.con.commit()
        cur.close()
    def save_search_query(self, query, category):
        """Save search queries for history"""
        cur = self.con.cursor()
        try:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS search_history (
                    id INTEGER PRIMARY KEY,
                    query TEXT,
                    category TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cur.execute('INSERT INTO search_history (query, category) VALUES (?, ?)', (query, category))
            self.con.commit()
        except Exception as e:
            print(f"Error saving search query: {e}")
        finally:
            cur.close()

    def get_search_history(self):
        """Retrieve saved search queries"""
        try:
            df = pd.read_sql("SELECT * FROM search_history ORDER BY timestamp DESC", self.con)
            return df
        except Exception as e:
            print(f"Error retrieving search history: {e}")
            return pd.DataFrame()

    def add_to_favorites(self, query, link, title, snippet):
        """Add a search result to favorites"""
        cur = self.con.cursor()
        try:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY,
                    query TEXT,
                    link TEXT,
                    title TEXT,
                    snippet TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(link)
                )
            ''')
            cur.execute('INSERT OR IGNORE INTO favorites (query, link, title, snippet) VALUES (?, ?, ?, ?)', 
                        (query, link, title, snippet))
            self.con.commit()
        except Exception as e:
            print(f"Error adding to favorites: {e}")
        finally:
            cur.close()

    def get_favorites(self):
        """Retrieve favorite search results"""
        try:
            df = pd.read_sql("SELECT * FROM favorites ORDER BY timestamp DESC", self.con)
            return df
        except Exception as e:
            print(f"Error retrieving favorites: {e}")
            return pd.DataFrame()
