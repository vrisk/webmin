#!/usr/local/bin/perl
# restart.cgi
# Restart the running named
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our (%access, %text, %in);

require './bind8-lib.pl';
&ReadParse();
$access{'ro'} && &error($text{'restart_ecannot'});
$access{'apply'} == 1 || $access{'apply'} == 3 ||
	&error($text{'restart_ecannot'});
&error_setup($text{'restart_err'});
my $err = &restart_bind();
&error($err) if ($err);

if ($access{'remote'}) {
	# Restart all secondarys too
	&error_setup();
	my @secondaryerrs = &restart_on_secondarys();
	if (@secondaryerrs) {
		&error(&text('restart_errsecondary',
		     "<p>".join("<br>", map { "$_->[0]->{'host'} : $_->[1]" }
				      	    @secondaryerrs)));
		}
	}

&webmin_log("apply");
&redirect($in{'zone'} && $in{'return'} ?
	  &redirect_url($in{'type'}, $in{'zone'}, $in{'view'}) : "");

