#!/usr/local/bin/perl
# create_primary.cgi
# Create a new primary zone
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
# Globals
our (%access, %text, %in, %config);

require './bind8-lib.pl';
&ReadParse();
&error_setup($text{'mcreate_err'});
$access{'primary'} || &error($text{'mcreate_ecannot'});
$access{'ro'} && &error($text{'primary_ero'});
my $conf = &get_config();
my ($view, $viewname, $vconf);
if ($in{'view'} ne '') {
	$view = $conf->[$in{'view'}];
	&can_edit_view($view) || &error($text{'primary_eviewcannot'});
	$vconf = $view->{'members'};
	$viewname = $view->{'values'}->[0];
	}
else {
	$vconf = $conf;
	$viewname = undef;
	}

# validate inputs
if ($in{'rev'}) {
	my $ipv4;
	($ipv4 = &check_net_ip($in{'zone'})) ||
	    $config{'support_aaaa'} &&
	    ($in{'zone'} =~ /^([\w:]+)(\/\d+)?$/ && &check_ip6address($1)) ||
		&error(&text('create_enet', $in{'zone'}));
	if ($ipv4) {
		$in{'zone'} = &ip_to_arpa($in{'zone'});
		}
	else {
		$in{'zone'} = &net_to_ip6int($1, ($2 ? substr($2, 1) : "" ));
		}
	}
else {
	($in{'zone'} =~ /^[\d\.]+$/ || $in{'zone'} =~ /^[\d\:]+(\/[\d]+)?$/) &&
		&error(&text('create_edom2', $in{'zone'}));
	&valdnsname($in{'zone'}, 0, ".") ||
		&error(&text('create_edom', $in{'zone'}));
	}
$in{'zone'} =~ s/\.$//;
&valdnsname($in{'primary'}, 0, ".") ||
	&error(&text('primary_eprimary', $in{'primary'}));
if ($in{'primary'} !~ /\.$/) { $in{'primary'} .= "."; }
&valemail($in{'email'}) || &valemail(&dotted_to_email($in{'email'})) ||
	&error(&text('primary_eemail', $in{'email'}));
$in{'email'} = &email_to_dotted($in{'email'});
$in{'refresh'} =~ /^\d+$/ ||
        &error(&text('primary_erefresh', $in{'refresh'}));
$in{'retry'} =~ /^\d+$/ ||
        &error(&text('primary_eretry', $in{'retry'}));
$in{'expiry'} =~ /^\d+$/ ||
        &error(&text('primary_eexpiry', $in{'expiry'}));
$in{'minimum'} =~ /^\d+$/ ||
        &error(&text('primary_eminimum', $in{'minimum'}));
my $base = $access{'dir'} ne '/' ? $access{'dir'} :
	$config{'primary_dir'} ? $config{'primary_dir'} :
				&base_directory($conf);
$base =~ s/\/+$// if ($base ne '/');
if ($base !~ /^([a-z]:)?\//) {
	# primary dir is relative .. make absolute
	$base = &base_directory()."/".$base;
	}
if ($in{'tmpl'}) {
	for(my $i=0; $config{"tmpl_$i"}; $i++) {
		my @c = split(/\s+/, $config{"tmpl_$i"}, 3);
		if ($c[1] eq 'A' && !$c[2] && !&check_ipaddress($in{'ip'})) {
			&error($text{'primary_eip'});
			}
		}
	}
foreach my $z (&find("zone", $vconf)) {
	if (lc($z->{'value'}) eq lc($in{'zone'})) {
		&error($text{'primary_etaken'});
		}
	}
if (!$in{'file_def'}) {
	$in{'file'} =~ /^\S+$/ ||
		&error(&text('create_efile', $in{'file'}));
	if ($in{'file'} !~ /^\//) {
		$in{'file'} = $base."/".$in{'file'};
		}
	&allowed_zone_file(\%access, $in{'file'}) ||
		&error(&text('create_efile2', $in{'file'}));
	}
else {
	$in{'file'} = &automatic_filename($in{'zone'}, $in{'rev'}, $base,
					  $view ? $view->{'value'} : undef);
	}
-r &make_chroot($in{'file'}) && &error(&text('create_efile4', $in{'file'}));
my @mips;
if ($in{'onsecondary'}) {
	@mips = split(/\s+/, $in{'mip'});
	@mips || &error($text{'primary_emips'});
	foreach my $m (@mips) {
		&check_ipaddress($m) || &error(&text('primary_emip', $m));
		}
	}

# Create the zone file and initial records
&create_primary_records($in{'file'}, $in{'zone'}, $in{'primary'}, $in{'email'},
		       $in{'refresh'}.$in{'refunit'},
		       $in{'retry'}.$in{'retunit'},
		       $in{'expiry'}.$in{'expunit'},
		       $in{'minimum'}.$in{'minunit'},
		       $in{'primary_ns'},
		       $in{'onsecondary'} && $access{'remote'},
		       $in{'tmpl'}, $in{'ip'}, $in{'addrev'});

if ($config{'relative_paths'}) {
	# Make path relative to BIND base directory
	my $bdir = &base_directory($conf);
	$in{'file'} =~ s/^\Q$bdir\/\E//;
	}

# create the zone directive
my $dir = { 'name' => 'zone',
	 'values' => [ $in{'zone'} ],
	 'type' => 1,
	 'members' => [ { 'name' => 'type',
			  'values' => [ 'primary' ] },
			{ 'name' => 'file',
			  'values' => [ $in{'file'} ] } ]
	};

# Add also-notify for secondarys
if ($in{'onsecondary'}) {
	my @secondarys = &list_secondary_servers();
	if (@secondarys) {
		my $also = { 'name' => 'also-notify',
			     'type' => 1,
			     'members' => [ ] };
		my $allow = { 'name' => 'allow-transfer',
			      'type' => 1,
			      'members' => [ ] };
		foreach my $s (@secondarys) {
			push(@{$also->{'members'}},
                             { 'name' => &to_ipaddress($s->{'host'}) });
			push(@{$allow->{'members'}},
                             { 'name' => &to_ipaddress($s->{'host'}) });
			}
		push(@{$dir->{'members'}}, $also);
		push(@{$dir->{'members'}}, $allow);
		push(@{$dir->{'members'}}, { 'name' => 'notify',
					     'values' => [ 'yes' ] });
		}
	}

# create the zone
&create_zone($dir, $conf, $in{'view'});
&webmin_log("create", "primary", $in{'zone'}, \%in);

&add_zone_access($in{'zone'});

# Create on secondary servers
if ($in{'onsecondary'} && $access{'remote'}) {
	my @secondaryerrs = &create_on_secondarys($in{'zone'}, $mips[0],
			$in{'sfile_def'} == 1 ? "none" :
			$in{'sfile_def'} == 2 ? undef : $in{'sfile'},
			undef, $viewname);
	if (@secondaryerrs) {
		&error(&text('primary_errsecondary',
		     "<p>".join("<br>", map { "$_->[0]->{'host'} : $_->[1]" }
				      	    @secondaryerrs)));
		}
	}

# Automatically sign zone if required 
if (&have_dnssec_tools_support() && $in{'enable_dt'}) {
	my $err;
	my $nsec3 = 0;
	my $zone = &get_zone_name($in{'zone'},
			$in{'view'} eq '' ? 'ANY' : $in{'view'});

	if ($zone) {
		if ($in{'dne'} eq "NSEC") {
			$nsec3 = 0;
		} elsif ($in{'dne'} eq "NSEC3") {
			$nsec3 = 1;
		} else {
			&error($text{'dt_zone_edne'});
		}

		# Sign zone 
		$err = &dt_sign_zone($zone, $nsec3);
		&error($err) if ($err);
	}
}

&redirect("edit_primary.cgi?zone=$in{'zone'}&view=$in{'view'}");

