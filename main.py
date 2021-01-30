import runpy


def main():
    app_package = runpy.run_module(
        mod_name="src.frigga", init_globals=globals())
    app_package['main']()


if __name__ == "__main__":
    main()
