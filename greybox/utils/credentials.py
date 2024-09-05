def in_colab():
    """Whether we are running in a colab notebook. This will attempt to import the google.colab package.

    Returns:
        bool: whether code is running in a colab notebook
    """
    try:
        import google.colab as _  # noqa

        return True
    except ImportError:
        return False
