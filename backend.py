import psycopg2

# Text formatter

class Formatter():
    # Format user profile data and return str
    def format_profile(self, data: dict) -> str:
        formatted_text = """
<b>First Name:</b>   {}
<b>Balance:</b>   {}
<b>Rate:</b>   {}
<b>Level:</b>   {}""".format(data["first_name"], data["balance"], data["rate"], data["level"])
        return formatted_text
    
    def format_job(self, data: dict) -> str:
        formmated_text = """
<b>First Name:</b>       {}
<b>Balance:</b>      {}
        """.format(data["title"], data["discription"])
        return formmated_text






# Backend with postgres

class Db():
    def __init__(self, db_host: str, db_port: str, db_user: str, db_password: str, db_database: str) -> None:
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.db_database = db_database
    
    def change_db(self, db_host: str,  db_port: str, db_user: str, db_password: str, db_database: str) -> None:
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.db_database = db_database

    # check if user is registered in the db
    def is_user_registered(self, chat_id: int) -> bool:
        connection = psycopg2.connect(host=self.db_host, port=self.db_port, user=self.db_user, password=self.db_password, database=self.db_database)
        cursor = connection.cursor()
        ret = False
        try:
            # check if the chat_id exists
            cursor.execute("SELECT EXISTS (SELECT chat_id FROM users WHERE chat_id = {})".format(chat_id))
            results = cursor.fetchone()[0]
            if results == True:
                ret = True
        except Exception as e:
            pass
        finally:
            connection.close()

        return ret

    def register(self, chat_id: int, phone_number: str, first_name: str, username: str) -> bool:
        connection = psycopg2.connect(host=self.db_host, port=self.db_port, user=self.db_user,password=self.db_password,database=self.db_database)
        cursor = connection.cursor()
        ret = False
        try:
            cursor.execute("INSERT INTO users(chat_id,phone_number,first_name,username) VALUES(%s,%s,%s,%s)",(chat_id, phone_number, first_name, username))
            connection.commit()
            ret = True
        except Exception as e:
            pass
        finally:
            connection.close()
        return ret

    def get_profile(self, chat_id: int) -> dict:
        connection = psycopg2.connect(host=self.db_host, port=self.db_port, user=self.db_user,password=self.db_password,database=self.db_database)
        cursor = connection.cursor()
        ret = {}
        try:
            # check if the chat_id exists
            cursor.execute("SELECT first_name, balance, money_made, verified, jobs_completed, rate, level FROM users WHERE chat_id = {}".format(chat_id))
            ret = cursor.fetchone()
            if ret == None or len(ret) == 0:
                ret = {}
            else:
                ret = {
                    "first_name": ret[0],
                    "balance": ret[1],
                    "money_made": ret[2],
                    "verified": ret[3],
                    "jobs_completed": ret[4],
                    "rate": ret[5],
                    "level": ret[6],
                }
        except Exception as e:
            pass
        finally:
            connection.close()
        return ret

    # adds a job into a job queue
    def add_job(self, chat_id: int, job_title: int) -> bool:
        connection = psycopg2.connect(host=self.db_host, port=self.db_port, user=self.db_user,password=self.db_password,database=self.db_database)
        cursor = connection.cursor()
        ret = False
        try:
            cursor.execute("INSERT INTO jobs(chat_id, title, status) VALUES(%s, %s, 'title')", (chat_id, job_title))
            connection.commit()
            ret = True
        except Exception as e:
            pass
        finally:
            connection.close()
        
        return ret

    # adds a job discription into a job
    def add_job_discription(self, chat_id: int, text: str) -> bool:
        connection = psycopg2.connect(host=self.db_host, port=self.db_port, user=self.db_user,password=self.db_password,database=self.db_database)
        cursor = connection.cursor()
        ret = False
        try:
            cursor.execute("SELECT job_id FROM jobs WHERE chat_id={} and status='title'".format(chat_id))
            job_id = cursor.fetchone()
            if job_id != None and len(job_id) > 0:
                cursor.execute("UPDATE jobs SET discription=%s, status='discription' WHERE job_id=%s",(text, job_id[0]))
                connection.commit()
                ret = True
        except Exception as e:
            pass
        finally:
            connection.close()
        
        return ret

    def get_job(self, chat_id: int) -> dict:
        connection = psycopg2.connect(host=self.db_host, port=self.db_port, user=self.db_user,password=self.db_password,database=self.db_database)
        cursor = connection.cursor()
        ret = {}
        try:
            cursor.execute("SELECT job_id, title, discription FROM jobs WHERE chat_id={} and status='discription'".format(chat_id))
            ret = cursor.fetchone()
            if ret == None or len(ret) == 0:
                ret = {}
            else:
                ret = {
                    "job_id": ret[0],
                    "title": ret[1],
                    "discription": ret[2],
                }
            
        except Exception as e:
            print(e)
        finally:
            connection.close()
        
        return ret
    
    def get_job_with_id(self, job_id: int) -> dict:
        connection = psycopg2.connect(host=self.db_host, port=self.db_port, user=self.db_user,password=self.db_password,database=self.db_database)
        cursor = connection.cursor()
        ret = {}
        try:
            cursor.execute("SELECT job_id, title, discription FROM jobs WHERE job_id={}".format(job_id))
            ret = cursor.fetchone()
            if ret == None or len(ret) == 0:
                ret = {}
            else:
                ret = {
                    "job_id": ret[0],
                    "title": ret[1],
                    "discription": ret[2],
                }
            
        except Exception as e:
            print(e)
        finally:
            connection.close()
        
        return ret
