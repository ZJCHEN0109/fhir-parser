import configparser


def ensure_init_py(settings, version_info):
    """ """
    init_tpl = """# _*_ coding: utf-8 _*_\n\n__fhir_version__ = "{0}"\n""".format(
        version_info.version
    )

    for file_location in [
        settings.RESOURCE_TARGET_DIRECTORY,
        settings.UNITTEST_TARGET_DIRECTORY,
    ]:

        if (file_location / "__init__.py").exists():
            lines = list()
            has_fhir_version = False
            with open((file_location / "__init__.py"), "r") as fp:
                for line in fp:
                    if "__fhir_version__" in line:
                        has_fhir_version = True
                        parts = list()
                        parts.append(line.split("=")[0])
                        parts.append('"{0}"'.format(version_info.version))

                        line = "= ".join(parts)
                    lines.append(line.rstrip("\n"))

            if not has_fhir_version:
                lines.append('__fhir_version__ = "{0}"'.format(version_info.version))

            txt = "\n".join(lines)
        else:
            txt = init_tpl

        with open((file_location / "__init__.py"), "w") as fp:
            fp.write(txt)


def update_pytest_fixture(settings):
    """ """
    lines = list()
    fixture_file = settings.RESOURCE_TARGET_DIRECTORY / "tests" / "fixtures.py"
    with open(str(fixture_file), "r", encoding="utf-8") as fp:
        for line in fp:
            if "ROOT_PATH =" in line:
                parts = list()
                parts.append(line.split("=")[0])
                parts.append(
                    "dirname(dirname(dirname(dirname(dirname(os.path.abspath(__file__))))))\n"
                )
                line = "= ".join(parts)

            elif "CACHE_PATH =" in line:
                parts = list()
                parts.append(line.split("=")[0])
                parts.append(f"os.path.join(ROOT_PATH, '.cache', '{settings.CURRENT_VERSION}')\n")
                line = "= ".join(parts)

            elif "example_data_file_uri =" in line:

                parts = list()
                parts.append(line.split("=")[0])
                parts.append(
                    f"'/'.join([settings['base_url'], "
                    f"'{settings.CURRENT_VERSION}', 'examples-json.zip'])\n"
                )
                line = "= ".join(parts)

            lines.append(line)

    # let's write
    fixture_file.write_text("".join(lines))

    with open(
        str(settings.RESOURCE_TARGET_DIRECTORY / "tests" / "conftest.py"), "w", encoding="utf-8"
    ) as fp:
        fp.write(
            "# _*_ coding: utf-8 _*_\n"
            f"pytest_plugins = ['fhir.resources.{settings.CURRENT_VERSION}.tests.fixtures']\n"
        )


def get_cached_version_info(spec_source):
    """ """
    if not spec_source.exists():
        return
    version_file = spec_source / "version.info"

    if not version_file.exists():
        return

    config = configparser.ConfigParser()

    with open(str(version_file), "r") as fp:
        txt = fp.read()
        config.read_string("\n".join(txt.split("\n")[1:]))

    return config["FHIR"]["version"], config["FHIR"]["fhirversion"]