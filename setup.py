from distutils.core import setup
setup(
    name = 'cleartag',
    packages = ['cleartag', 'cleartag.enums'],
    version = '1.1.0',
    description = 'Audio metadata library providing a transparent interface for reading and writing MP3, FLAC, and other popular formats',
    url = 'https://github.com/spiritualized/cleartag',
    download_url = 'https://github.com/spiritualized/cleartag/archive/v1.1.0.tar.gz',
    keywords = ['metadata', 'mp3', 'flac', 'lame', 'python', 'library'],
    install_requires = [
                    'bitstring>=3.1.6',
                    'mutagen>=1.42.0',
                ],

    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
