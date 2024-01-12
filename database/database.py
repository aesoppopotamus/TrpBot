import pymysql
import os
from apscheduler.triggers.interval import IntervalTrigger
from utils.utils import create_repeating_task


class Database:
    def __init__(self, bot, scheduler):
        self.bot = bot
        self.scheduler = scheduler
        self.dbhost = os.getenv('DBHOST')
        self.dbuser = os.getenv('DBUSER')
        self.dbpass = os.getenv('DBPASS')
        self.database = os.getenv('DBNAME')

    ##lookup 
    def stored_repeating_messages(self):
        connection = pymysql.connect(host=self.dbhost, user=self.dbuser, password=self.dbpass, database=self.database, cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM scheduled_repeating_messages"
                cursor.execute(sql)

                repeating_messages = cursor.fetchall()
                for message in repeating_messages:
                    channel_id = message['channel_id']
                    message_content = message['message_content']
                    interval_unit = message['interval_unit']
                    interval_value = message['interval_value']
                    job_id = message['job_id']

        except Exception as e:
            print(f"Error queueing repeating messages: {e}")
        finally:
            connection.close()  

    ##queue up existing records from db
    async def queue_repeating_messages(self):
        connection = pymysql.connect(host=self.dbhost, user=self.dbuser, password=self.dbpass, database=self.database, cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM scheduled_repeating_messages"
                cursor.execute(sql)

                repeating_messages = cursor.fetchall()
                for message in repeating_messages:
                    channel_id = message['channel_id']
                    message_content = message['message_content']
                    interval_unit = message['interval_unit']
                    interval_value = message['interval_value']
                    job_id = message['job_id']
                    username = message['scheduled_by']

                    trigger = IntervalTrigger(**{interval_unit: interval_value})
                    self.scheduler.add_job(create_repeating_task, trigger, args=[self.bot, channel_id, message_content, username], id=job_id)    
        except Exception as e:
            print(f"Error queueing repeating messages: {e}")
        finally:
            connection.close()
    
    async def queue_repeating_cmds(self):
        connection = pymysql.connect(host=self.dbhost, user=self.dbuser, password=self.dbpass, database=self.database, cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM scheduled_commands"
                cursor.execute(sql)

                repeating_messages = cursor.fetchall()
                for message in repeating_messages:
                    channel_id = message['channel_id']
                    command_content = message['command_content']
                    interval_unit = message['interval_unit']
                    interval_value = message['interval_value']
                    job_id = message['job_id']
                    username = message['scheduled_by']

                    trigger = IntervalTrigger(**{interval_unit: interval_value})
                    self.scheduler.add_job(create_repeating_task, trigger, args=[self.bot, channel_id, command_content, username], id=job_id)    
        except Exception as e:
            print(f"Error queueing repeating messages: {e}")
        finally:
            connection.close()

    def add_scheduled_message(self, channel_id, message, interval_unit, interval_value, job_id, username):
        connection = pymysql.connect(host=self.dbhost, user=self.dbuser, password=self.dbpass, database=self.database, cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO scheduled_repeating_messages (channel_id, message_content, interval_unit, interval_value, job_id, scheduled_by) VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (channel_id, message, interval_unit, interval_value, job_id, username))
            connection.commit()
        except Exception as e:
            print(f"Failed to schedule message: {e}")
        finally:
            connection.close()  

    def add_scheduled_command(self, channel_id, command_content, interval_unit, interval_value, job_id, username):
        connection = pymysql.connect(host=self.dbhost, user=self.dbuser, password=self.dbpass, database=self.database, cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                sql = """
                INSERT INTO scheduled_commands (channel_id, command_content, interval_unit, interval_value, job_id, scheduled_by) VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (channel_id, command_content, interval_unit, interval_value, job_id, username))
            connection.commit()
        except Exception as e:
            print(f"Failed to schedule message: {e}")
        finally:
            connection.close()  

    def get_scheduled_messages(self):
        connection = pymysql.connect(host=self.dbhost, user=self.dbuser, password=self.dbpass, database=self.database, cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM scheduled_repeating_messages"
                cursor.execute(sql)
                schedules = cursor.fetchall()
                return schedules
        except Exception as e:
            print(f"An error occurred: {e}")
            return []    
        finally:
            connection.close()  


    def get_scheduled_cmds(self):
        connection = pymysql.connect(host=self.dbhost, user=self.dbuser, password=self.dbpass, database=self.database, cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM scheduled_commands"
                cursor.execute(sql)
                schedules = cursor.fetchall()
                return schedules
        except Exception as e:
            print(f"An error occurred: {e}")
            return []    
        finally:
            connection.close()  

    def delete_scheduled_message(self, job_id):
        connection = pymysql.connect(host=self.dbhost, user=self.dbuser, password=self.dbpass, database=self.database, cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM scheduled_repeating_messages WHERE job_id = %s"
                cursor.execute(sql, (job_id,))
                rows_affected = cursor.rowcount
            connection.commit()
            return rows_affected > 0  # Return True if a row was affected

        except Exception as e:
            print(f"Failed to remove job from database: {e}")  # Log the exception
            return False
        finally:
            connection.close()  

    def delete_scheduled_command(self, job_id):
        connection = pymysql.connect(host=self.dbhost, user=self.dbuser, password=self.dbpass, database=self.database, cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM scheduled_commands WHERE job_id = %s"
                cursor.execute(sql, (job_id,))
                rows_affected = cursor.rowcount
            connection.commit()
            return rows_affected > 0  # Return True if a row was affected

        except Exception as e:
            print(f"Failed to remove job from database: {e}")  # Log the exception
            return False
        finally:
            connection.close() 
