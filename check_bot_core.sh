#!/bin/bash

echo "Running Discord Bot Module Check..."
echo "--------------------------------"
echo "✓ Core modules check starting"

python3 -c "import bot; print('✓ Bot module imported successfully')" || echo "✗ Failed to import bot module"
python3 -c "import watchdog; print('✓ Watchdog module imported successfully')" || echo "✗ Failed to import watchdog module"
python3 -c "import config; print('✓ Config module imported successfully')" || echo "✗ Failed to import config module"
python3 -c "import logger; print('✓ Logger module imported successfully')" || echo "✗ Failed to import logger module"

echo "--------------------------------"
echo "✓ Core modules check complete"
echo "→ Needs actual Discord credentials to run"
