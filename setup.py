from setuptools import setup, find_packages

setup(
    name="tuxtalks",
    version="1.0.0b1",
    description="A privacy-focused voice assistant for Linux gamers",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Startux",
    url="https://github.com/Startux/tuxtalks",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Topic :: Games/Entertainment",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
    ],
    packages=find_packages(),
    py_modules=[
        "config", "model_manager", "tuxtalks", "launcher",
        "game_manager", "lal_manager", "i18n",  # Internationalization support
        "rtl_layout",  # RTL language layout helpers
        "ipc_server", "ipc_client", "runtime_menu",  # Hybrid CLI/GUI architecture
        "launcher_speech_tab", "launcher_player_tab", "launcher_games_tab",
        "launcher_corrections_tab", "launcher_input_tab", "launcher_vocabulary_tab",
        "launcher_training_tab", # NEW: Training tab for launcher
        "launcher_packs_tab",
        "logger",  # Debug logging system
        "ollama_handler",  # Ollama AI integration
        "voice_fingerprint",  # Voice learning system
        "player_interface",  # Player interface base class
        "voice_manager", "input_controller", "input_listener",  # Core components
        "local_library", "help_content",  # Utilities
        "launcher_setup_wizard",  # NEW: First-run setup wizard
        "tuxtalks_admin",  # NEW: Administrative toolbox
    ],
    include_package_data=True,
    package_data={
        '': [
            'theme/sv_ttk/*.tcl',
            'data/*.json',  # System corrections
            'locale/*/LC_MESSAGES/*.mo'
        ],
    },
    data_files=[
        ('locale/es/LC_MESSAGES', ['locale/es/LC_MESSAGES/tuxtalks.mo', 'locale/es/LC_MESSAGES/tuxtalks.po']),
        ('locale/uk/LC_MESSAGES', ['locale/uk/LC_MESSAGES/tuxtalks.mo', 'locale/uk/LC_MESSAGES/tuxtalks.po']),
        ('locale/cy/LC_MESSAGES', ['locale/cy/LC_MESSAGES/tuxtalks.mo', 'locale/cy/LC_MESSAGES/tuxtalks.po']),
        ('locale/de/LC_MESSAGES', ['locale/de/LC_MESSAGES/tuxtalks.mo', 'locale/de/LC_MESSAGES/tuxtalks.po']),
        ('locale/fr/LC_MESSAGES', ['locale/fr/LC_MESSAGES/tuxtalks.mo', 'locale/fr/LC_MESSAGES/tuxtalks.po']),
        ('locale/ar/LC_MESSAGES', ['locale/ar/LC_MESSAGES/tuxtalks.mo', 'locale/ar/LC_MESSAGES/tuxtalks.po']),
    ],
    install_requires=[
        "vosk",
        "pyaudio",  # For voice training recording
        "requests",
        "dbus-python",
        "mutagen>=1.45.1",
        "evdev>=1.7.0",
        "zeroconf>=0.131.0",
        "piper-tts>=1.2.0",
        "sv-ttk>=2.5.0",  # Sun Valley Theme
        "soundfile>=0.12.1",
        "simpleaudio>=1.0.4",
        "numpy>=1.24.0",
        "psutil>=5.9.0",
        "wyoming>=1.8.0",
        "pynput>=1.7.6",
        "ttkbootstrap",
        "defusedxml>=0.7.1",
        "Babel>=2.13.0",  # i18n/gettext support
    ],
    entry_points={
        "console_scripts": [
            "tuxtalks=tuxtalks:main",  # Primary entry point (Defaults to CLI)
            "tuxtalks-gui=launcher:main",  # Main settings & configuration
            "tuxtalks-menu=runtime_menu:main",  # Runtime selection window
            "tuxtalks-admin=tuxtalks_admin:main",  # NEW: Toolbox for maintenance
        ],
    },
)
