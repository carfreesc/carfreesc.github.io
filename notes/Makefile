LOCAL=./html_output
LIVE=../docs

PANDOC_COMMON=--template=template.html -s
PANDOC_GUIDE=$(PANDOC_COMMON) --toc --toc-depth=3

all: index gettinghere gettingaround tips

$(LOCAL):
	mkdir -p $(LOCAL)

index: | $(LOCAL)
	pandoc $(PANDOC_COMMON) index.md --metadata title="Car-free State College" --metadata leaflet=true -o $(LOCAL)/index.html
	cp $(LOCAL)/index.html $(LIVE)/

gettinghere: | $(LOCAL)
	pandoc $(PANDOC_GUIDE) gettinghere.md --metadata title="Getting to State College" -o $(LOCAL)/gettinghere.html
	cp $(LOCAL)/gettinghere.html $(LIVE)/

gettingaround: | $(LOCAL)
	pandoc $(PANDOC_GUIDE) gettingaround.md --metadata title="Getting around State College" -o $(LOCAL)/gettingaround.html
	cp $(LOCAL)/gettingaround.html $(LIVE)/

tips: | $(LOCAL)
	pandoc $(PANDOC_GUIDE) tips.md --metadata title="Tips for car-free living" -o $(LOCAL)/tips.html
	cp $(LOCAL)/tips.html $(LIVE)/

.PHONY: all index gettinghere gettingaround tips
