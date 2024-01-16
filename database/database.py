import pymysql
import os
import datetime
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
    
    ## scheduled message CRUD
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

# Gameplan CRUD operations
            
    def add_gameplan_month(self, channel_id, planning_header, planning_content, planning_month, username):
        connection = pymysql.connect(host=self.dbhost, user=self.dbuser, password=self.dbpass, database=self.database, cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO monthly_planning (channel_id, planning_header, planning_content, planning_month, username) VALUES (%s, %s, %s, %s, %s)
                    """
                cursor.execute(sql, (channel_id, planning_header, planning_content, planning_month, username))
                rows_affected = cursor.rowcount
                connection.commit()
                return rows_affected > 0
            
        except Exception as e:
            print(f"Failed to store plan: {e}")
        finally:
            connection.close()

    def get_gameplan_month(self, planning_month):
        connection = pymysql.connect(host=self.dbhost, user=self.dbuser, password=self.dbpass, database=self.database, cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                sql = "SELECT * FROM monthly_planning WHERE planning_month = %s"
                cursor.execute(sql, (planning_month,))
                gameplan = cursor.fetchall()
                return gameplan
        except Exception as e:
            print(f"An error occurred: {e}")
            return []    
        finally:
            connection.close()
    
    def overwrite_gameplan_byid(self, gameplan_id, planning_month, planning_content):
        connection = pymysql.connect(host=self.dbhost, user=self.dbuser, password=self.dbpass, database=self.database, cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                sql = """
                    UPDATE monthly_planning
                    SET planning_content = %s, planning_month = %s, last_modified = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """
                cursor.execute(sql, (planning_content, planning_month, gameplan_id))
                connection.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Failed to update gameplan: {e}")
            return False
        finally:
            connection.close()
                
    def append_to_gameplan(self, gameplan_id, additional_content):
        connection = pymysql.connect(host=self.dbhost, user=self.dbuser, password=self.dbpass, database=self.database, cursorclass=pymysql.cursors.DictCursor)
        try:
            with connection.cursor() as cursor:
                # First, get the current content
                select_sql = "SELECT planning_content FROM monthly_planning WHERE id = %s"
                cursor.execute(select_sql, (gameplan_id,))
                result = cursor.fetchone()
                if result:
                    current_content = result['planning_content']
                    new_content = current_content + "\n" + additional_content  # Append new content

                    # Now, update the content
                    update_sql = """
                        UPDATE monthly_planning 
                        SET planning_content = %s, last_modified = CURRENT_TIMESTAMP
                        WHERE id = %s
                        """
                    cursor.execute(update_sql, (new_content, gameplan_id))
                    connection.commit()
                    return cursor.rowcount > 0
                else:
                    return False
        except Exception as e:
            print(f"Failed to append to gameplan: {e}")
            return False
        finally:
            connection.close()