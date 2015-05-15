local ffi = require "ffi"
local S = require "syscall"
local c = S.c
local t = S.types.t
local util = S.util
local nr = require "syscall.linux.nr"
local lfs = require "syscall.lfs"

-- Returns an iterator over open fds
local function open_fds(pid)
	if pid then
		pid = string.format("%d", pid)
	else
		pid = "self"
	end
	local iter, state, last = assert(lfs.dir("/proc/" .. pid .. "/fd"))
	return function(state)
		while true do
			last = iter(state, last)
			if last == nil then
				return nil
			elseif last:match("^%d+$") then
				local fd = tonumber(last)
				if fd ~= state.fd:getfd() then
					return fd
				end
			end
		end
	end, state
end

local function syscall_filter(syscalls)
	local program = {
		-- test architecture correct
		t.sock_filter("LD,W,ABS", ffi.offsetof(t.seccomp_data, "arch")),
		t.sock_filter("JMP,JEQ,K", util.auditarch(), 1, 0),
		t.sock_filter("RET,K", c.SECCOMP_RET.KILL),
		-- get syscall number
		t.sock_filter("LD,W,ABS", ffi.offsetof(t.seccomp_data, "nr")),
	}
	for i, v in ipairs(syscalls) do
		table.insert(program, t.sock_filter("JMP,JEQ,K", nr.SYS[v], 0, 1))
		table.insert(program, t.sock_filter("RET,K", c.SECCOMP_RET.ALLOW))
	end
	-- TODO: allow opening files read only
	-- else kill
	table.insert(program, t.sock_filter("RET,K", c.SECCOMP_RET.KILL))

	local pp = t.sock_filters(#program, program)
	local p = t.sock_fprog1{{#program, pp}}
	return p
end

local function protect()
	-- Close open fds
	for fd in open_fds() do
		if fd ~= 1 and fd ~= 2 then -- don't close stdout or stderr
      print(fd)
		end
	end
	assert(S.prctl("set_no_new_privs", true))
	local nnp = assert(S.prctl("get_no_new_privs"))
	assert(nnp == 1)
	S.unshare("files,fs,newipc,newnet,newns,newuts,sysvsem") -- Don't assert this, usually we don't have permissions to unshare
	assert(S.setrlimit("AS", { max = 8*1024 })) -- 8 MB memory limit
	assert(S.setrlimit("CORE", { max = 0 })) -- no core dumps
	assert(S.setrlimit("CPU", { max = 3 })) -- 3 second runtime limit
	assert(S.setrlimit("FSIZE", { max = 0 })) -- can't create files larger than 0 bytes
	assert(S.setrlimit("MSGQUEUE", { max = 0 })) -- no POSIX message queues
	assert(S.setrlimit("NOFILE", { max = 1 })) -- can't open more than 1 file
	assert(S.setrlimit("NPROC", { max = 0 })) -- no forking
	assert(S.prctl("set_dumpable", 0))
	--assert(S.prctl("set_securebits", "keep_caps_locked,no_setuid_fixup,no_setuid_fixup_locked,noroot,noroot_locked"))
	assert(S.prctl("set_seccomp", "filter", syscall_filter {
		"rt_sigaction",
		-- Cleanup
		"exit_group",
		"close",
		-- Memory management
		"mprotect",
		(nr.SYS.mmap2 and "mmap2" or "mmap"),
		"munmap",
		"brk",
		-- Output
		"write",
		"fstat",
	}))
end

return {
	protect = protect;
}
