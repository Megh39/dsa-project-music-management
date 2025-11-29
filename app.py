# %%
import csv
from flask import Flask,render_template,request
# ----------------------------------------------------
# SONG CLASS
# ----------------------------------------------------
class Song:
    def __init__(self, song_id, title, artist, album, genre, duration, year):
        self.song_id = song_id
        self.title = title
        self.artist = artist
        self.album = album
        self.genre = genre
        self.duration = int(duration)
        self.year = int(year)

    def __repr__(self):
        return f"[{self.song_id}] {self.title} by {self.artist} ({self.album}, {self.year}) - {self.genre}, {self.duration}s"



# %%

# ----------------------------------------------------
# HASH TABLE FOR SONG LIBRARY
# ----------------------------------------------------
class HashNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.next = None


class HashTable:
    def __init__(self, size=100):
        self.size = size
        self.table = [None] * size

    def _hash(self, key):
        h = 5381
        for c in key:
            h = ((h << 5) + h) + ord(c)
        return h % self.size

    def insert(self, key, value):
        index = self._hash(key)
        node = self.table[index]

        if not node:
            self.table[index] = HashNode(key, value)
            return

        while node.next:
            if node.key == key:
                node.value = value
                return
            node = node.next

        node.next = HashNode(key, value)

    def search(self, key):
        index = self._hash(key)
        node = self.table[index]

        while node:
            if node.key == key:
                return node.value
            node = node.next
        return None
    def search_by_title(self, title):
        matches = []
        for bucket in self.table:
            node = bucket
            while node:
                if node.value.title.lower() == title.lower():
                    matches.append(node.value)
                node = node.next
        return matches
    def search_by_partial_title(self, partial):
        matches = []
        partial = partial.lower()
        for bucket in self.table:
            node = bucket
            while node:
                if partial in node.value.title.lower():
                    matches.append(node.value)
                node = node.next
        return matches

    def delete(self, key):
        index = self._hash(key)
        node = self.table[index]
        prev = None

        while node:
            if node.key == key:
                if prev:
                    prev.next = node.next
                else:
                    self.table[index] = node.next
                return True
            prev, node = node, node.next

        return False

    def display(self):
        for i in range(self.size):
            node = self.table[i]
            if node:
                print(f"Bucket {i}: ", end="")
                chain = []
                while node:
                    chain.append(node.key)
                    node = node.next
                print(" -> ".join(chain))


# %%


# ----------------------------------------------------
# LINKED LIST FOR PLAYLIST
# ----------------------------------------------------
class Node:
    def __init__(self, song):
        self.song = song
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None

    def insert_at_start(self, song):
        new_node = Node(song)
        new_node.next = self.head
        self.head = new_node

    def insert_at_end(self, song):
        new_node = Node(song)
        if not self.head:
            self.head = new_node
            return
        current = self.head
        while current.next:
            current = current.next
        current.next = new_node

    def delete_song(self, song_id):
        current = self.head
        prev = None

        while current and current.song.song_id != song_id:
            prev = current
            current = current.next

        if not current:
            print("Song not found.")
            return False

        if not prev:
            self.head = current.next
        else:
            prev.next = current.next

        print("Deleted:", current.song.title)
        return True

    def search(self, song_id):
        current = self.head
        while current:
            if current.song.song_id == song_id:
                return current.song
            current = current.next
        return None
    def search_by_title(self, title):
        title = title.lower()
        current = self.head
        results = []

        while current:
            if current.song.title.lower() == title:
                results.append(current.song)
            current = current.next

        return results

    def search_by_partial_title(self, partial):
        partial = partial.lower()
        current = self.head
        results = []

        while current:
            if partial in current.song.title.lower():
                results.append(current.song)
            current = current.next

        return results

    def display(self):
        if not self.head:
            print("Playlist is empty.")
            return
        out=[]
        current = self.head
        while current:
            out.append(str(current.song))
            current = current.next
        return "\n".join(out)


# %%

# ----------------------------------------------------
# QUEUE FOR PLAYBACK
# ----------------------------------------------------
class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, song):
        self.items.append(song)
        return f"Added to queue: {song.title}"

    def dequeue(self):
        if not self.items:
            return "Queue empty.", None
        song = self.items.pop(0)
        return f"Now playing: {song.title}", song

    def peek(self):
        if not self.items:
            return None
        return self.items[0]

    def display(self):
        if not self.items:
            return "Queue is empty."

        out = ["Current Queue:"]
        for i, song in enumerate(self.items, start=1):
            out.append(f"{i}. {song.title} by {song.artist}")

        return "\n".join(out)
    def find_song_for_queue(text):
        # ID
        s = library.search(text)
        if s: return s

        # full title
        exact = library.search_by_title(text)
        if exact: return exact[0]

        # partial
        partial = library.search_by_partial_title(text)
        if partial: return partial[0]

        return None


# %%


# ----------------------------------------------------
# STACK FOR RECENTLY PLAYED
# ----------------------------------------------------
class Stack:
    def __init__(self):
        self.items = []

    def push(self, song):
        self.items.append(song)

    def pop(self):
        if not self.items:
            print("No recently played songs.")
            return None
        return self.items.pop()
    def display_list(self):
        if not self.items:
            return "No recently played songs."
        return "\n".join(str(s) for s in reversed(self.items))

    def display(self):
        if not self.items:
            print("No recently played songs.")
            return
        print("Recently Played:")
        for song in reversed(self.items):
            print(song)



# %%

# ----------------------------------------------------
# LOAD SONGS FROM CSV
# ----------------------------------------------------
def load_songs(filename):
    songs = []
    with open(filename, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            song = Song(
                row["song_id"],
                row["title"],
                row["artist"],
                row["album"],
                row["genre"],
                int(row["duration_sec"]),
                int(row["release_year"])
            )
            songs.append(song)
    return songs



songs = load_songs("songs_dataset_updated.csv")


library = HashTable(size=60)
playlist = LinkedList()
queue = Queue()
history = Stack()

# Insert all into hash table
for s in songs:
    library.insert(s.song_id, s)

# ----------------------------------------------------
# FLASK APP
# ----------------------------------------------------
app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")
# ---------------------- LIBRARY ----------------------
@app.route("/library", methods=["POST"])
def library_action():
    song_id = request.form.get("song_id")
    action = request.form.get("action")

    # ---------------- SEARCH ----------------
    if action == "search":
        q = song_id.strip()

        # 1. try exact ID
        by_id = library.search(q)
        if by_id:
            return render_template(
                "index.html",
                library_output=str(by_id),
                active_section="library-section"
            )

        # 2. try full title match
        by_title = library.search_by_title(q)
        if by_title:
            out = "\n".join(str(s) for s in by_title)
            return render_template(
                "index.html",
                library_output=out,
                active_section="library-section"
            )

        # 3. try partial title
        by_partial = library.search_by_partial_title(q)
        if by_partial:
            out = "\n".join(str(s) for s in by_partial)
            return render_template(
                "index.html",
                library_output=out,
                active_section="library-section"
            )

        return render_template(
            "index.html",
            library_output="No match found.",
            active_section="library-section"
        )

    # ---------------- DELETE ----------------
    elif action == "delete":
        ok = library.delete(song_id)
        return render_template(
            "index.html",
            library_output="Deleted." if ok else "Not found.",
            active_section="library-section"
        )


@app.route("/library/display", methods=["POST"])
def library_display():
    output = library.display()
    return render_template(
        "index.html",
        library_output=output,
        active_section="library-section"
    )



# ---------------------- PLAYLIST ----------------------
@app.route("/playlist", methods=["POST"])
def playlist_action():
    song_id = request.form.get("song_id")
    action = request.form.get("action")

    song = library.search(song_id)
    if not song:
        return render_template(
            "index.html",
            playlist_output="Song not found in library.",
            active_section="playlist-section"
        )

    if action == "add_start":
        playlist.insert_at_start(song)
        return render_template(
            "index.html",
            playlist_output="Inserted at start.",
            active_section="playlist-section"
        )

    elif action == "add_end":
        playlist.insert_at_end(song)
        return render_template(
            "index.html",
            playlist_output="Inserted at end.",
            active_section="playlist-section"
        )

    elif action == "delete":
        removed = playlist.delete_song(song_id)
        return render_template(
            "index.html",
            playlist_output="Deleted." if removed else "Song not found.",
            active_section="playlist-section"
        )



@app.route("/playlist/display", methods=["POST"])
def playlist_display():
    return render_template(
    "index.html",
    playlist_output=playlist.display(),
    active_section="playlist-section"
)




# ---------------------- QUEUE ----------------------
def find_song(text):
    # id match
    s = library.search(text)
    if s:
        return s

    # exact title
    t = library.search_by_title(text)
    if t:
        return t[0]

    # partial title
    p = library.search_by_partial_title(text)
    if p:
        return p[0]

    return None

@app.route("/queue", methods=["POST"])
def queue_action():
    song_id = request.form.get("song_id")
    action = request.form.get("action")

    # -------- ENQUEUE --------
    if action == "enqueue":
        song = find_song(song_id)
        if not song:
            return render_template(
                "index.html",
                queue_output="Song not found.",
                active_section="queue-section"
            )
        msg = queue.enqueue(song)
        return render_template(
            "index.html",
            queue_output=msg,
            active_section="queue-section"
        )

    # -------- DEQUEUE / PLAY NEXT --------
    elif action == "dequeue":
        msg, song = queue.dequeue()
        if song:
            history.push(song)
        return render_template(
            "index.html",
            queue_output=msg,
            active_section="queue-section"
        )

    # -------- PEEK --------
    elif action == "peek":
        song = queue.peek()
        return render_template(
            "index.html",
            queue_output=(str(song) if song else "Queue empty."),
            active_section="queue-section"
        )


@app.route("/queue/display", methods=["POST"])
def queue_display():
    return render_template(
        "index.html",
        queue_output=queue.display(),
        active_section="queue-section"
    )



# ---------------------- HISTORY ----------------------
@app.route("/history", methods=["POST"])
def history_action():
    action = request.form.get("action")

    if action == "undo":
        song = history.pop()
        if not song:
            return render_template(
                "index.html",
                history_output="History empty.",
                active_section="history-section"
            )

        queue.enqueue(song)
        return render_template(
            "index.html",
            history_output=f"Restored to queue: {song.title}",
            active_section="history-section"
        )

    elif action == "clear":
        history.items.clear()
        return render_template(
            "index.html",
            history_output="History cleared.",
            active_section="history-section"
        )


@app.route("/history/display", methods=["POST"])
def history_display():
   return render_template("index.html",
                       history_output=history.display_list(),
                       active_section="history-section")


# ----------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)