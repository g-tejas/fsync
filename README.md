# f(ast)-sync

- Uses io_uring
- SIMD
- Supports up to protocol ?
- Uses HTTP to bypass most firewalls

## Ideas
E.g., running an rsync if a 10m files hierarchy usually requires 10m synchronous stat calls. Using io-uring would make them asynchronous, but they could potentially be done more efficiently (e.g. convert file names to inodes in blocks of 20k, and then stat those 20k inodes in a batch).
That would require e.g. the VFS layer to support batch operations. But the io-uring would actually allow that without a user space interface change.

# Fancy words
- **Server**: The host providing the data
- **Client**: The host that will get the synced data

# The Meat
Suppose we run the command `rsync src dest`
1. Split the dest into chunks of length `n`
2. Calculate weak (adler32) and strong (md5) checksum for each chunk of dest (can be empty)
3. Send those to the host(server) that has src file
4. Find all chunks of length `n` in src that are in dest by comparing checksums
5. Create a list of instructions to generate src from dest


## Other notable implementations
- [fast_rsync](https://github.com/dropbox/fast_rsync/tree/master) by DropBox
    - "A faster implementation of librsync in pure Rust, using SIMD operations where available"

# Todo
- [] Remove generators and `yield` entirely, just use lists so we can know the amount of changes
- [] Implement in C++ obviously
