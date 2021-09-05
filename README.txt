To use an open source library:
1. Install the library inside your project:

    1.1. Inside your project navigate to <project>\venv\Lib\site-packages
    1.2. Open bash here
    1.3. Run command: pip install yfinance -t ./
                Here the actual command is   pip install <package_name> -t <any/path/i/like>

                Note: you can actually only run pip install <pkg_name> and then from the project open venv/Lib/site-packages.
                If you see the pkg here then pcharm will pick it up.

    Note: pip install <library_name>   ==> Will install library in C:\Python27\Lib\site-packages. You don't want this.

    Note: use "pip" to install for Python27 and "pip3" to install for Python36

    1.4. For xlsx writer. run cmd " pip install xlsxwriter -t ./" to install xlsx writer
    1.5. For beautiful soup, run cmd " pip install beautifulsoup4 -t ./ --no-user"

2. Now you can use it inside your program
    import <library_name>