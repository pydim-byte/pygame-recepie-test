[app]
# (str) Title of your application
title = SampleApp
# (str) Package name
package.name = nfsApk
# (str) Package domain (needed for android/ios packaging)
package.domain = org.novfensec
# (str) Source code where the main.py live
source.dir = .
# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas
# (list) List of inclusions using pattern matching
source.include_patterns = images/*.png
# (str) Application versioning (method 1)
version = 0.1

# (list) Application requirements
requirements = python3==3.12.8, hostpython3==3.12.8, cython, pygame-ce

# (list) Supported orientations
orientation = portrait

# Android specific
fullscreen = 0
android.api = 36
android.minapi = 30
android.accept_sdk_license = True

# (list) The Android archs to build for
android.archs = arm64-v8a

android.allow_backup = True
android.release_artifact = aab
android.debug_artifact = apk

# Python for android (p4a) specific
p4a.branch = develop
p4a.local_recipes = ./p4a-recepies

[buildozer]
log_level = 2
warn_on_root = 1
