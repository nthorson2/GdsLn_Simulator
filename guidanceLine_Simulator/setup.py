from setuptools import setup

setup(name='pnts_to_bound',
      version='0.1.0',
      description='Generate Guidance Lines file based on desired swath width',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
          'Operating System :: OS Independent'
      ],
      url='http://github.com/nthorson2/GIS-Tools/guidanceLine_Simulator',
      author='Nathan Thorson',
      author_email='nthorson2@unl.edu',
      license='MIT',
      packages=['pnts_to_bound'],
      install_requires=[],
      include_package_data=True,
      zip_safe=False)