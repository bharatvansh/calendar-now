#!/usr/bin/env python3
"""
Setup script for Calendar Now
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
def read_readme():
    here = os.path.abspath(os.path.dirname(__file__))
    try:
        with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "A user-friendly application for managing Google Calendar events from the system tray."

# Read requirements
def read_requirements():
    here = os.path.abspath(os.path.dirname(__file__))
    try:
        with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        return [
            'PyQt5>=5.15.0',
            'google-auth>=2.15.0',
            'google-auth-oauthlib>=0.8.0',
            'google-api-python-client>=2.70.0',
            'cryptography>=3.4.8',
            'requests>=2.25.1',
            'python-dateutil>=2.8.2'
        ]

setup(
    name='calendar-now',
    version='1.0.0',
    author='Calendar Now Team',
    author_email='contact@calendarnow.com',
    description='A user-friendly application for managing Google Calendar events from the system tray.',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/your-username/calendar-now',
    project_urls={
    'Bug Reports': 'https://github.com/your-username/calendar-now/issues',
    'Source': 'https://github.com/your-username/calendar-now',
    },
    
    # Package configuration
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    package_data={
        '': ['*.svg', '*.ico', '*.png', '*.jpg'],
        'resources': ['icons/*'],
    },
    
    # Dependencies
    install_requires=read_requirements(),
    python_requires='>=3.7',
    
    # Entry points
    entry_points={
        'console_scripts': [
            'calendar-now=main:main',
        ],
        'gui_scripts': [
            'calendar-now-gui=main:main',
        ],
    },
    
    # Metadata
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Office/Business :: Scheduling',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Environment :: X11 Applications :: Qt',
        'Environment :: Win32 (MS Windows)',
        'Environment :: MacOS X',
    ],
    
    keywords='calendar google-calendar desktop-app qt pyqt5 productivity scheduling',
    
    # Additional metadata
    zip_safe=False,
    platforms=['Windows', 'macOS', 'Linux'],
    
    # Optional dependencies
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-qt>=4.0',
            'pytest-cov>=2.10',
            'black>=21.0',
            'flake8>=3.8',
            'mypy>=0.800',
            'pre-commit>=2.15',
        ],
        'build': [
            'pyinstaller>=4.5',
            'cx_Freeze>=6.8',
            'auto-py-to-exe>=2.20',
        ],
        'windows': [
            'pywin32>=227',
            'winshell>=0.6',
        ],
    },
    
    # Data files (for system-wide installation)
    data_files=[
    ('share/applications', ['calendar-now.desktop']) if os.name == 'posix' else None,
        ('share/pixmaps', ['resources/icons/app_icon.svg']) if os.name == 'posix' else None,
    ] if os.name == 'posix' else [],
)

# Post-installation message
print("""
✅ Calendar Now has been installed successfully!

🚀 To get started:
    1. Run 'calendar-now' from your terminal or application menu
   2. Follow the setup wizard to connect your Google Calendar
   3. The app will appear in your system tray

📖 For help and documentation, visit:
    https://github.com/your-username/calendar-now

🐛 Report issues at:
    https://github.com/your-username/calendar-now/issues

Thank you for using Calendar Now! 🎉
""")