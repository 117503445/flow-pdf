use notify::{
    event::{AccessKind, AccessMode},
    Config, EventKind, RecommendedWatcher, RecursiveMode, Watcher,
};
use serde::Deserialize;
use std::io::Read;
use std::path::Path;
use std::{collections::HashMap, fs::File};

#[derive(Deserialize, Debug)]
#[allow(dead_code)]
struct Trigger {
    prefix: String,
    suffix: String,
}

#[derive(Deserialize, Debug)]
#[allow(dead_code)]
struct Action {
    r#type: String,
    args: HashMap<String, String>,
}

#[derive(Deserialize, Debug)]
#[allow(dead_code)]
struct Rule {
    triggers: Vec<Trigger>,
    actions: Vec<Action>,
}

fn main() {
    // let path = std::env::args()
    //     .nth(1)
    //     .expect("Argument 1 needs to be a path");

    let mut file = File::open("rule.json").expect("Failed to open rule.json");
    let mut contents = String::new();
    file.read_to_string(&mut contents)
        .expect("Failed to read rule.json");
    let rule: Rule = serde_json::from_str(&contents).expect("Failed to parse JSON");
    println!("rule: {:?}", rule);

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
