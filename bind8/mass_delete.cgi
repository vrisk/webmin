#!/usr/local/bin/perl
# Delete a bunch of zones, after asking for confirmation
use strict;
use warnings;
no warnings 'redefine';
no warnings 'uninitialized';
our (%access, %text, %in);

require './bind8-lib.pl';
&ReadParse();
my $conf = &get_config();

my $dparams = join("&", map { "d=".&urlize($_) } split(/\0/, $in{'d'}));
if ($in{'update'}) {
	# Redirect to mass update form
	&redirect("mass_update_form.cgi?".$dparams);
	exit;
	}
elsif ($in{'create'}) {
	# Redirect to mass create form
	&redirect("mass_rcreate_form.cgi?".$dparams);
	exit;
	}
elsif ($in{'rdelete'}) {
	# Redirect to mass record delete form
	&redirect("mass_rdelete_form.cgi?".$dparams);
	exit;
	}

# Get the zones
my (@zones, @znames);
foreach my $d (split(/\0/, $in{'d'})) {
	my ($zonename, $viewidx) = split(/\s+/, $d);
	my $zone = &get_zone_name_or_error($zonename, $viewidx);
	my ($view, $zconf);
	if ($zone->{'viewindex'} ne '') {
		$view = $conf->[$zone->{'viewindex'}];
		$zconf = $view->{'members'}->[$zone->{'index'}];
		}
	else {
		$zconf = $conf->[$zone->{'index'}];
		}
	&can_edit_zone($zone) ||
		&error($text{'primary_edelete'});
	push(@zones, [ $zconf, $view ]);
	push(@znames, $zconf->{'value'});
	}
$access{'ro'} && &error($text{'primary_ero'});
$access{'delete'} || &error($text{'primary_edeletecannot'});

if (!$in{'confirm'}) {
	# Ask the user if he is sure
	&ui_print_header(undef, $text{'massdelete_title'}, "");

	# Check if any are used by Virtualmin
	my @doms;
	foreach my $z (@znames) {
		push(@doms, &get_virtualmin_domains($z));
		}
	my $vwarn;
	if (@doms) {
		my $f = "<tt>$doms[0]->{'dom'}</tt>";
		$vwarn = @doms == 1 ? &text('massdelete_vwarn', $f)
				    : &text('massdelete_vwarn2', $f, @doms-1);
		}

	my @servers = &list_secondary_servers();
	print &ui_confirmation_form("mass_delete.cgi",
		&text('massdelete_rusure', scalar(@zones),
		      join(", ", @znames)),
		[ map { [ "d", $_ ] } split(/\0/, $in{'d'}) ],
		[ [ 'confirm', $text{'massdelete_ok'} ] ],
		@servers && $access{'remote'} ?
			$text{'delete_onsecondary'}." ".
			&ui_yesno_radio("onsecondary", 1) : "",
		$vwarn,
		);

	&ui_print_footer("", $text{'index_return'});
	}
else {
	# Do it!
	&ui_print_unbuffered_header(undef, $text{'massdelete_title'}, "");

	foreach my $zi (@zones) {
		my $zconf = $zi->[0];
		my $view = $zi->[1];
		my $type = &find_value("type", $zconf->{'members'});
		print &text('massdelete_zone', $zconf->{'value'}),"<br>\n";

		# delete the records file
		my $f = &find("file", $zconf->{'members'});
		if ($f && $type ne 'hint') {
			&delete_records_file($f->{'value'});
			}

		# delete any keys
		&delete_dnssec_key($zconf, 0);

		# remove the zone directive
		&lock_file(&make_chroot($zconf->{'file'}));
		&save_directive($view || &get_config_parent($zconf->{'file'}),
				[ $zconf ], [ ]);
		print $text{'massdelete_done'},"<p>\n";

		# Also delete from secondary servers
		if ($in{'onsecondary'} && $access{'remote'}) {
			my $viewname = $view ? $view->{'values'}->[0] : undef;
			print &text('massdelete_secondarys',
				    $zconf->{'value'}),"<br>\n";
			my @secondaryerrs = &delete_on_secondarys(
				$zconf->{'value'}, undef, $viewname);
			if (@secondaryerrs) {
				print $text{'massdelete_failed'},"<br>\n";
				foreach my $s (@secondaryerrs) {
					print "$s->[0]->{'host'} : $s->[1]<br>\n";
					}
				print "<p>\n";
				}
			else {
				print $text{'massdelete_done'},"<p>\n";
				}
			}
		}
	&flush_file_lines();
	&unlock_all_files();
	&webmin_log("delete", "zones", scalar(@zones));

	&ui_print_footer("", $text{'index_return'});
	}

