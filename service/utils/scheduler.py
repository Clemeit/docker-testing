import schedule
import threading
import time


def run_on_schedule(event: callable, interval: int) -> tuple[callable, callable]:
    # Schedule the task to run every 5 seconds
    schedule.every(interval).seconds.do(event)

    # Create an event to control the scheduler thread
    stop_event = threading.Event()

    def run_schedule():
        while not stop_event.is_set():
            schedule.run_pending()
            time.sleep(1)

    scheduler_thread = threading.Thread(target=run_schedule)
    scheduler_thread.daemon = True

    def start_schedule():
        """Start the scheduler thread."""
        if not scheduler_thread.is_alive():
            event()
            scheduler_thread.start()
            print("Scheduler started.")

    def stop_schedule():
        """Stop the scheduler thread."""
        stop_event.set()
        scheduler_thread.join()
        print("Scheduler stopped.")

    return start_schedule, stop_schedule
