# Fabric workspace synchronization

This is the Git integration folder for native Fabric items synchronized from
the `entreprise-sales-data-hub` workspace.

Fabric creates and updates its own item folders and metadata here. Don't move
standalone `.py` or `.sql` source files into this folder; Git integration
doesn't turn arbitrary files into Fabric workspace items. Keep application
source, tests, CI configuration, and synthetic input data in their existing
repository directories.

Connect the workspace to the `fabric-poc` branch and set the Git folder to
`fabric_workspace`. The workspace already contains the PoC items. On the
initial sync, choose to commit the workspace content to Git so those items are
exported; updating the workspace from Git instead can replace existing
workspace content.

Git integration versions supported Fabric item definitions, not the data
stored in Lakehouse tables. Keep the synthetic source data in
`data/raw/sales/` and load it into the Bronze Lakehouse separately.
