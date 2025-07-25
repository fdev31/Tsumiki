import os

import setproctitle
from fabric import Application
from fabric.utils import exec_shell_command, get_relative_path
from loguru import logger

import utils.functions as helpers
from modules.bar import StatusBar
from utils.colors import Colors
from utils.config import theme_config, widget_config
from utils.constants import APP_CACHE_DIRECTORY, APPLICATION_NAME


@helpers.run_in_thread
def process_and_apply_css(app: Application):
    logger.info(f"{Colors.INFO}[Main] Compiling CSS")
    output = exec_shell_command("sass styles/main.scss dist/main.css --no-source-map")

    if output == "":
        logger.info(f"{Colors.INFO}[Main] CSS applied")
        app.set_stylesheet_from_file(get_relative_path("dist/main.css"))
    else:
        logger.exception(f"{Colors.ERROR}[Main]Failed to compile sass!")
        logger.exception(f"{Colors.ERROR}[Main] {output}")
        app.set_stylesheet_from_string("")


general_options = widget_config["general"]
module_options = widget_config["modules"]

if not general_options["debug"]:
    for log in [
        "fabric",
        "widgets",
        "utils",
        "utils.config",
        "modules",
        "services",
    ]:
        logger.disable(log)


def main():
    """Main function to run the application."""

    helpers.ensure_directory(APP_CACHE_DIRECTORY)
    helpers.copy_theme(theme_config["name"])
    helpers.check_executable_exists("sass")

    # Create the status bar
    bar = StatusBar(widget_config)

    windows = [bar]

    if module_options["notification"]["enabled"]:
        from modules.notification import NotificationPopup

        windows.append(NotificationPopup(widget_config))

    if module_options["screen_corners"]["enabled"]:
        from modules.corners import ScreenCorners

        screen_corners = ScreenCorners(widget_config)

        windows.append(screen_corners)

    if module_options["quotes"]["enabled"]:
        from modules.quotes import DesktopQuote

        quotes = DesktopQuote(widget_config)

        windows.append(quotes)

    if module_options["dock"]["enabled"]:
        from modules.dock import Dock

        dock = Dock(widget_config)

        windows.append(dock)

    if module_options["desktop_clock"]["enabled"]:
        from modules.desktop_clock import DesktopClock

        desktop_clock = DesktopClock(widget_config)

        windows.append(desktop_clock)

    if module_options["osd"]["enabled"]:
        from modules.osd import OSDContainer

        windows.append(OSDContainer(widget_config))

    # Initialize the application with the status bar
    app = Application(APPLICATION_NAME, windows=windows)

    setproctitle.setproctitle(APPLICATION_NAME)

    if general_options["debug"]:
        helpers.set_debug_logger()

    process_and_apply_css(app)

    # Run the application
    app.run()

    logger.info(f"{Colors.INFO}[Main] Starting {APPLICATION_NAME}...")
    logger.info(f"Starting shell... pid:{os.getpid()}")


if __name__ == "__main__":
    main()
