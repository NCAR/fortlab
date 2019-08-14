
def main():
    import os
    from setuptools import setup, find_packages
    from pyloco import collect_mgrattrs

    here = os.path.abspath(os.path.dirname(__file__))
    mgr = collect_mgrattrs(os.path.join(here, "fortlab", "main.py"), "FortLab")

    setup(
        name=mgr.get("_name_"),
        version=mgr.get("_version_"),
        description=mgr.get("_description_", None),
        long_description=mgr.get("_long_description_", None),
        author=mgr.get("_author_", None),
        author_email=mgr.get("_author_email_", None),
        license=mgr.get("_license_", None),
        packages=find_packages(),
        install_requires=["pyloco"],
        url=mgr.get("_url_", None),
        entry_points={
            'console_scripts': [
                'fortlab = fortlab:main'
            ]
        },
        classifiers=[
            'Intended Audience :: Developers',
            'Natural Language :: English',
            'Development Status :: 1 - Planning',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Topic :: Software Development :: Code Generators']
        )

if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()
    main()
