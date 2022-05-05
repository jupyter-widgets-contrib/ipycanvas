from tempfile import mkdtemp

c.ServerApp.port = 8888  # noqa: F821
c.ServerApp.token = ""  # noqa: F821
c.ServerApp.password = ""  # noqa: F821
c.ServerApp.disable_check_xsrf = True  # noqa: F821
c.ServerApp.open_browser = False  # noqa: F821
c.ServerApp.root_dir = mkdtemp(prefix="galata-test-")  # noqa: F821

c.LabApp.expose_app_in_browser = True  # noqa: F821
