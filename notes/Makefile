LOCAL=./html_output
LIVE=../docs

all: index gettinghere gettingaround tips

index:
	pandoc --template=template.html index.md --metadata title="Car-free State College: Index" -s -o $(LOCAL)/index.html
	cp $(LOCAL)/index.html $(LIVE)/

gettinghere:
	pandoc --template=template.html gettinghere.md --metadata title="Getting to State College" -s -o $(LOCAL)/gettinghere.html
	cp $(LOCAL)/gettinghere.html $(LIVE)/

gettingaround:
	pandoc --template=template.html gettingaround.md --metadata title="Getting around State College" -s -o $(LOCAL)/gettingaround.html
	cp $(LOCAL)/gettingaround.html $(LIVE)/

tips:
	pandoc --template=template.html tips.md --metadata title="Tips for car-free living" -s -o $(LOCAL)/tips.html
	cp $(LOCAL)/tips.html $(LIVE)/

.PHONY: all index gettinghere gettingaround tips
