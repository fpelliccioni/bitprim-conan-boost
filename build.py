from conan.packager import ConanMultiPackager
import os

if __name__ == "__main__":
    builder = ConanMultiPackager(username="bitprim", channel="stable")
    builder.add_common_builds(shared_option_name="bitprim-conan-boost:shared")
    builder.password = os.getenv("CONAN_PASSWORD")
    filtered_builds = []
    for settings, options, env_vars, build_requires in builder.builds:
        if settings["build_type"] == "Release":
             filtered_builds.append([settings, options, env_vars, build_requires])
    builder.builds = filtered_builds
    builder.run()