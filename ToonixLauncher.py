import sys
from launcher.bootstrap import main

if __name__ == "__main__":
    if "--test-boot" in sys.argv:
        print("BOOT_OK")
        sys.exit(0)
    main()
