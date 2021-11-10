SLINKY_PREFIX = "slinky:"
SLINKY_CURSOR_KEY = f"{SLINKY_PREFIX}cursor"
BATCH_SIZE = 200  # Only insert this many datasets at  time
BACKOFF_SIZE = 100  # Don't enqueue more add_dataset_jobs unless there are fewer than this many jobs in the dataset queue
CURSOR_EPOCH = "1900-01-01T00:00:00.000Z"
