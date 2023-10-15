use notify::{
    event::{AccessKind, AccessMode},
    Config, EventKind, RecommendedWatcher, RecursiveMode, Watcher,
};
use std::path::Path;

fn main() {
    // let path = std::env::args()
    //     .nth(1)
    //     .expect("Argument 1 needs to be a path");

    let path = "/data";

    println!("Watching {path}");

    if let Err(error) = watch(path) {
        println!("Error: {error:?}");
    }
}

fn watch<P: AsRef<Path>>(path: P) -> notify::Result<()> {
    let (tx, rx) = std::sync::mpsc::channel();

    // Automatically select the best implementation for your platform.
    // You can also access each implementation directly e.g. INotifyWatcher.
    let mut watcher = RecommendedWatcher::new(tx, Config::default())?;

    // Add a path to be watched. All files and directories at that path and
    // below will be monitored for changes.
    watcher.watch(path.as_ref(), RecursiveMode::Recursive)?;

    for res in rx {
        match res {
            Ok(event) => {
                if event.kind == EventKind::Access(AccessKind::Close(AccessMode::Write)) {
                    println!("Change: {event:?}");
                    let paths = event.paths;
                    println!("path: {:?}", paths);
                }
            }
            Err(error) => println!("Error: {error:?}"),
        }
    }

    Ok(())
}
